import random
from dataclasses import dataclass
from typing import List, Dict, Set, Literal


# 個体
@dataclass
class Individual:
    id: int
    text: str
    wins: int = 0
    losses: int = 0
    fitness: float = 0.0
    generation: int = 0


# 人間選好ログの選択肢（none なし）
Choice = Literal["A", "B"]


# ペア比較の記録
@dataclass
class PairLog:
    pair_id: int
    indiv_a_id: int
    indiv_b_id: int
    chosen: Choice  # "A" か "B" だけ


# 文字列をどの文字集合から作るか（ひらがなのみ）
CHARSET = (
    "あいうえおかきくけこさしすせそたちつてとなにぬねの"
    "はひふへほまみむめもやゆよらりるれろわをんっゃゅょ"
)


def random_string(min_len: int = 10, max_len: int = 40) -> str:
    length = random.randint(min_len, max_len)
    return "".join(random.choice(CHARSET) for _ in range(length))


def initialize_population(size: int, generation: int = 0) -> List[Individual]:
    population: List[Individual] = []
    for i in range(size):
        population.append(
            Individual(
                id=i,
                text=random_string(),
                generation=generation,
            )
        )
    return population


def compute_fitness(population: List[Individual], epsilon: float = 1e-6) -> None:
    """wins / (wins + losses) から fitness を計算"""
    for ind in population:
        total = ind.wins + ind.losses
        if total == 0:
            ind.fitness = 0.0
        else:
            ind.fitness = ind.wins / (total + epsilon)


def select_parents(population: List[Individual]) -> Individual:
    """フィットネスに比例した確率で1個体を選ぶ（ルーレット選択）"""
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
    mutation_rate の確率で、ランダム位置の1文字を置換。
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

    # エリート保存（wins / losses / fitness もコピー）
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

    # 残りを交叉＋変異で埋める（子どもは wins/losses 0 からスタート）
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
            # 例えば、別世代のIDが混ざっている場合などはスキップ
            continue

        if log.chosen == "A":
            a.wins += 1
            b.losses += 1
        elif log.chosen == "B":
            b.wins += 1
            a.losses += 1
        # Choice は "A" or "B" のみなので "none" ケースはない


# テスト用：人間の代わりに「適当なルール」でログを作る
def generate_dummy_logs(population: List[Individual], num_pairs: int) -> List[PairLog]:
    logs: List[PairLog] = []
    for pair_id in range(num_pairs):
        a, b = random.sample(population, 2)

        # ここは好きな「擬似人間ルール」に変えてOK
        # 例: 文字列長が長いほうを勝ちとする
        score_a = len(a.text)
        score_b = len(b.text)

        if score_a > score_b:
            chosen: Choice = "A"
        elif score_b > score_a:
            chosen = "B"
        else:
            # 同点ならランダムにどちらかを選ぶ
            chosen = random.choice(["A", "B"])

        logs.append(
            PairLog(
                pair_id=pair_id,
                indiv_a_id=a.id,
                indiv_b_id=b.id,
                chosen=chosen,
            )
        )
    return logs

if __name__ == "__main__":
    random.seed(0)

    pop = initialize_population(size=5, generation=0)
    print("初期 wins:", [ind.wins for ind in pop])

    # ダミーログ作成（長さで勝ち負けを決める）
    logs = generate_dummy_logs(pop, num_pairs=10)

    aggregate_results_from_logs(pop, logs)
    print("集計後 wins:", [ind.wins for ind in pop])
    print("集計後 losses:", [ind.losses for ind in pop])

    compute_fitness(pop)
    print("fitness:", [round(ind.fitness, 3) for ind in pop])
if __name__ == "__main__":
    random.seed(0)

    pop = initialize_population(size=200, generation=0)

    num_generations = 10

    for gen in range(num_generations):
        print(f"=== Generation {gen} ===")

        # 1. ログを集める（今はダミー。将来ここが「人間選好」になる）
        logs = generate_dummy_logs(pop, num_pairs=1000)

        # 2. ログから wins / losses を集計
        aggregate_results_from_logs(pop, logs)

        # デバッグ確認したければここで一度表示
        print("wins の一部:", [ind.wins for ind in pop[:10]])

        # 3. 進化ステップ（次世代を作る）
        pop = evolve_one_generation(
            population=pop,
            population_size=200,
            elite_size=20,
            mutation_rate=0.3,
            next_generation_index=gen + 1,
        )

        # 4. サンプル出力
        for ind in pop[:5]:
            print(ind.id, len(ind.text), ind.text[:50], "wins=", ind.wins, "fitness=", f"{ind.fitness:.3f}")
        print()
