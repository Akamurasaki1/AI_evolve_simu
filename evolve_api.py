import random
import json
from dataclasses import asdict
from typing import List

from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

# 進化エンジンから import
from evolve_engine import (
    Individual,
    Choice,
    PairLog,
    initialize_population,
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

LOG_PATH = "pair_logs.jsonl"


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
    log = PairLog(
        pair_id=req.pair_id,
        indiv_a_id=req.indiv_a_id,
        indiv_b_id=req.indiv_b_id,
        chosen=req.chosen,
    )
    append_pairlog_to_file(log)
    return {"status": "ok"}
