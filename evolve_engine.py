import random
from dataclasses import dataclass
from typing import List, Dict, Literal
from typing import Optional
from pydantic import BaseModel  # か dataclass か、実際の定義に合わせて

# 個体
@dataclass
class Individual:
    id: int
    text: str
    wins: int = 0
    losses: int = 0
    fitness: float = 0.0
    generation: int = 0


# 人間選好ログの選択肢
Choice = Literal["A", "B"]


# ペア比較の記録
@dataclass
class PairLog:
    pair_id: int
    indiv_a_id: int
    indiv_b_id: int
    chosen: Choice
    timestamp: Optional[str] = None  # ← これを追加（ISO 8601 の文字列）


# 文字集合
CHARSET = (
    "あいうえおかきくけこさしすせそたちつてとなにぬねの"
    "はひふへほまみむめもやゆよらりるれろわをんっゃゅょ"
)


def random_string(min_len: int = 10, max_len: int = 40) -> str:
    length = random.randint(min_len, max_len)
    return "".join(random.choice(CHARSET) for _ in range(length))


def initialize_population(size: int, generation: int = 0) -> List[Individual]:
    return [
        Individual(
            id=i,
            text=random_string(),
            generation=generation,
        )
        for i in range(size)
    ]


def compute_fitness(population: List[Individual], epsilon: float = 1e-6) -> None:
    """wins / (wins + losses) から fitness を計算"""
    for ind in population:
        total = ind.wins + ind.losses
        if total == 0:
            ind.fitness = 0.0
        else:
            ind.fitness = ind.wins / (total + epsilon)


def select_parents(population: List[Individual]) -> Individual:
    """フィットネスに比例した確���で1個体を選ぶ（ルーレット選択）"""
    total_fitness = sum(ind.fitness for ind in population)
    if total_fitness == 0:
        return random.choice(population)

    r = random.random() * total_fitness
    s = 0.0
    for ind in population:
        s += ind.fitness
        if s >= r:
            return ind
    return population[-1]


def crossover(s1: str, s2: str) -> str:
    """2つの文字列からランダムな位置 k で交叉"""
    if not s1:
        return s2
    if not s2:
        return s1
    k = random.randint(0, min(len(s1), len(s2)))
    return s1[:k] + s2[k:]


def mutate(text: str, mutation_rate: float = 0.3) -> str:
    """
    mutation_rate の確���で、ランダム位置の1文字を置換。
    例: mutation_rate=0.3 → 30%の確率で1文字だけ変異
    """
    if not text:
        return text
    if random.random() > mutation_rate:
        return text
    pos = random.randint(0, len(text) - 1)
    new_char = random.choice(CHARSET)
    return text[:pos] + new_char + text[pos + 1 :]


def evolve_one_generation(
    population: List[Individual],
    population_size: int,
    elite_size: int,
    mutation_rate: float,
    next_generation_index: int,
) -> List[Individual]:
    """
    wins / losses がすでに埋まっている前提で、
    fitness を計算し、1世代進化させる。
    """
    compute_fitness(population)

    population_sorted = sorted(population, key=lambda ind: ind.fitness, reverse=True)
    next_pop: List[Individual] = []

    # エリートを wins/losses/fitness ごとコピー
    for i in range(min(elite_size, len(population_sorted))):
        src = population_sorted[i]
        next_pop.append(
            Individual(
                id=len(next_pop),
                text=src.text,
                wins=src.wins,
                losses=src.losses,
                fitness=src.fitness,
                generation=next_generation_index,
            )
        )

    # 残りは新しい子ども（wins/losses 0 から）
    while len(next_pop) < population_size:
        parent1 = select_parents(population_sorted)
        parent2 = select_parents(population_sorted)
        child_text = crossover(parent1.text, parent2.text)
        child_text = mutate(child_text, mutation_rate=mutation_rate)
        next_pop.append(
            Individual(
                id=len(next_pop),
                text=child_text,
                wins=0,
                losses=0,
                fitness=0.0,
                generation=next_generation_index,
            )
        )

    return next_pop


def reset_scores(population: List[Individual]) -> None:
    """Individual の wins / losses を 0 にリセット"""
    for ind in population:
        ind.wins = 0
        ind.losses = 0


def build_id_map(population: List[Individual]) -> Dict[int, Individual]:
    """id -> Individual の辞書を作る（高速アクセス用）"""
    return {ind.id: ind for ind in population}


def aggregate_results_from_logs(
    population: List[Individual],
    logs: List[PairLog],
) -> None:
    """
    PairLog のリストから、各 Individual の wins / losses を更新する。
    population を in-place で書き換える。
    """
    reset_scores(population)
    id_map = build_id_map(population)

    for log in logs:
        a = id_map.get(log.indiv_a_id)
        b = id_map.get(log.indiv_b_id)
        if a is None or b is None:
            continue
        if log.chosen == "A":
            a.wins += 1
            b.losses += 1
        elif log.chosen == "B":
            b.wins += 1
            a.losses += 1
