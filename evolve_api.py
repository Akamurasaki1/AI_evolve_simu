import random
import json
from dataclasses import asdict
from typing import List

from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path

# 進化エンジンから import
from evolve_engine import (
    Individual,
    Choice,
    PairLog,
    initialize_population,
    aggregate_results_from_logs,
    evolve_one_generation,
)


# ============
# API の定義
# ============




app = FastAPI()

# CORS制限でfetchがブロックされている可能性があるのでこれで制限をゆるくする
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # 最初は全部許可でOK。あとで必要なら絞る
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# シンプルにメモリに現世代を持つ（起動時だけ初期化）
current_population: List[Individual] = initialize_population(size=200, generation=0)
next_pair_id = 0

LOG_PATH = Path("pair_logs.jsonl")

class LogEntry(BaseModel):
    pair_id: int
    indiv_a_id: int
    indiv_b_id: int
    chosen: str

@app.get("/debug/logs", response_model=List[LogEntry])
def get_logs(limit: int = 100):
    logs = []
    if LOG_PATH.exists():
        with LOG_PATH.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    d = json.loads(line)
                    logs.append(d)
                except Exception:
                    continue
    # 最後の limit 件だけ返す
    return logs[-limit:]

# Generation state management
# Note: This implementation is designed for single-user evaluation sessions.
# For multi-user concurrent access, consider adding threading.Lock() for thread safety.
EVALS_PER_GEN = 100  # Configurable: number of evaluations per generation
current_generation = 0
current_eval_count = 0


class IndivInfo(BaseModel):
    id: int
    text: str


class PairResponse(BaseModel):
    pair_id: int
    generation: int
    indiv_a: IndivInfo
    indiv_b: IndivInfo


class ChoiceRequest(BaseModel):
    pair_id: int
    indiv_a_id: int
    indiv_b_id: int
    chosen: Choice  # "A" or "B"


def append_pairlog_to_file(log: PairLog, path: str = LOG_PATH) -> None:
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(asdict(log), ensure_ascii=False) + "\n")


def load_logs_from_file(path: str = LOG_PATH) -> List[PairLog]:
    """Load all PairLog entries from the JSONL file."""
    logs = []
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    data = json.loads(line)
                    logs.append(PairLog(**data))
    except FileNotFoundError:
        pass  # No logs yet, return empty list
    return logs


def clear_logs_file(path: str = LOG_PATH) -> None:
    """Clear the log file by truncating it."""
    with open(path, "w", encoding="utf-8") as f:
        pass  # File is truncated when opened in write mode


@app.get("/pair", response_model=PairResponse)
def get_pair():
    """
    比較用のペアを1組返す。
    """
    global next_pair_id
    a, b = random.sample(current_population, 2)
    pair_id = next_pair_id
    next_pair_id += 1

    return PairResponse(
        pair_id=pair_id,
        generation=a.generation,
        indiv_a=IndivInfo(id=a.id, text=a.text),
        indiv_b=IndivInfo(id=b.id, text=b.text),
    )


@app.post("/choice")
def post_choice(req: ChoiceRequest):
    """
    ユーザーが A/B のどちらを選んだかを受け取り、ログファイルに追記する。
    """
    global current_eval_count
    
    log = PairLog(
        pair_id=req.pair_id,
        indiv_a_id=req.indiv_a_id,
        indiv_b_id=req.indiv_b_id,
        chosen=req.chosen,
    )
    append_pairlog_to_file(log)
    
    # Increment evaluation count for this generation
    current_eval_count += 1
    
    return {
        "status": "ok",
        "generation": current_generation,
        "eval_count": current_eval_count,
        "evals_per_gen": EVALS_PER_GEN,
    }


@app.get("/status")
def get_status():
    """
    Return current generation and evaluation counts.
    """
    return {
        "generation": current_generation,
        "eval_count": current_eval_count,
        "evals_per_gen": EVALS_PER_GEN,
    }


@app.post("/evolve")
def post_evolve():
    """
    Evolve to the next generation based on accumulated evaluation logs.
    
    Steps:
    1. Load all logs from pair_logs.jsonl
    2. Aggregate results to update wins/losses
    3. Evolve the population using evolve_one_generation
    4. Update server state (generation, eval_count, population)
    5. Clear the log file for the new generation
    """
    global current_population, current_generation, current_eval_count
    
    # Load logs
    logs = load_logs_from_file()
    
    # Aggregate results to update wins/losses
    aggregate_results_from_logs(current_population, logs)
    
    # Calculate evolution parameters
    population_size = len(current_population)
    elite_size = max(1, int(population_size * 0.1))  # 10% elite
    mutation_rate = 0.3
    next_generation_index = current_generation + 1
    
    # Evolve to next generation
    new_population = evolve_one_generation(
        population=current_population,
        population_size=population_size,
        elite_size=elite_size,
        mutation_rate=mutation_rate,
        next_generation_index=next_generation_index,
    )
    
    # Update server state
    old_generation = current_generation
    current_population = new_population
    current_generation = next_generation_index
    current_eval_count = 0
    
    # Clear the log file for the new generation
    clear_logs_file()
    
    return {
        "status": "ok",
        "old_generation": old_generation,
        "new_generation": current_generation,
        "population_size": population_size,
        "elite_size": elite_size,
        "mutation_rate": mutation_rate,
    }
