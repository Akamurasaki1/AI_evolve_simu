import random
import string
from dataclasses import dataclass
from typing import List


# 個体
@dataclass
class Individual:
    id: int
    text: str
    wins: int = 0
    losses: int = 0
    fitness: float = 0.0
    generation: int = 0


# 文字列をどの文字集合から作るか（ひとまずひらがな＋記号なども可）
CHARSET = (
    string.ascii_letters
    + " 。、「」"
    + "あいうえおかきくけこさしすせそたちつてとなにぬねの"
    + "はひふへほまみむめもやゆよらりるれろわをんっゃゅょ"
    + "1234567890"
    + "!@#$%^&*()-_=+[]{};:'\",.<>?/\\|`~"
)


def random_string(min_len: int = 10, max_len: int = 40) -> str:
    length = random.randint(min_len, max_len)
    return "".join(random.choice(CHARSET) for _ in range(length))


def initialize_population(size: int, generation: int = 0) -> List[Individual]:
    population = []
    for i in range(size):
        population.append(
            Individual(
                id=i,
                text=random_string(),
                generation=generation,
            )
        )
    return population


# ここは本来「人間のA/B選択」から埋まるが、テスト用にダミー評価を作ることもできる
def compute_fitness(population: List[Individual], epsilon: float = 1e-6) -> None:
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
        # 全員フィットネス0なら一様ランダム
        return random.choice(population)

    r = random.random() * total_fitness
    s = 0.0
    for ind in population:
        s += ind.fitness
        if s >= r:
            return ind
    return population[-1]


def crossover(s1: str, s2: str) -> str:
    # 2つの文字列からランダムな位置 k で交叉
    if not s1:
        return s2
    if not s2:
        return s1
    k = random.randint(0, min(len(s1), len(s2)))
    return s1[:k] + s2[k:]


def mutate(text: str, mutation_rate: float = 0.1) -> str:
    # mutation_rate の確率で、ランダム位置の1文字を別の文字に置換
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
    # 1. フ���ットネス計算（wins/losses は事前に埋まっている前提）
    compute_fitness(population)

    # 2. エリート選択
    population_sorted = sorted(population, key=lambda ind: ind.fitness, reverse=True)
    next_pop: List[Individual] = []

    # エリートをそのままコピー
    for i in range(min(elite_size, len(population_sorted))):
        ind = population_sorted[i]
        next_pop.append(
            Individual(
                id=len(next_pop),
                text=ind.text,
                generation=next_generation_index,
            )
        )

    # 3. 残りを交叉＋変異で埋める
    while len(next_pop) < population_size:
        parent1 = select_parents(population_sorted)
        parent2 = select_parents(population_sorted)
        child_text = crossover(parent1.text, parent2.text)
        child_text = mutate(child_text, mutation_rate=mutation_rate)
        next_pop.append(
            Individual(
                id=len(next_pop),
                text=child_text,
                generation=next_generation_index,
            )
        )

    return next_pop


def extract_ngrams(text: str, min_len: int = 3) -> set[str]: # 切り出す長さの最小
    """text から長さ min_len 以上の全ての部分文字列を集合として取り出す"""
    ngrams: set[str] = set()
    n = len(text)
    for length in range(min_len, n + 1):
        for i in range(0, n - length + 1):
            ngrams.add(text[i : i + length])
    return ngrams


if __name__ == "__main__":
    # random.seed(0)  # 毎回同じ進化を再現したければコメントアウトを外す

    pop = initialize_population(size=100, generation=0)

    hiragana_set = set(
        "あいうえおかきくけこさしすせそたちつてとなにぬねの"
        "はひふへほまみむめもやゆよらりるれろわをんっゃゅょ"
    )

    # お手本文章（好きなひらがな文に変えてOK）
    TARGET_TEXT = "わたしがりょうてをひろげても、おそらはちっともとべないが、とべることりはわたしのように、じめんをはやくははしれない。わたしがからだをゆすっても、きれいなおとはでないけど、あのなるすずはわたしのように、たくさんなうたはしらないよ。すずと、ことりと、それからわたし、みんなちがって、みんないい。"
    target_ngrams = extract_ngrams(TARGET_TEXT, min_len=3)

    num_generations = 100

    for gen in range(num_generations):
        for ind in pop:
            text = ind.text

            # ひらがな数（ベーススコア）
            hira_count = sum(1 for ch in text if ch in hiragana_set)

            # ngram マッチ数スコア
            ngram_score = 0
            n = len(text)
            for length in range(3, n + 1):
                for i in range(0, n - length + 1):
                    substr = text[i : i + length]
                    if substr in target_ngrams:
                        # マッチ1件ごとに加点（長い一致ほどボーナス大）
                        ngram_score += length

            # 最終的な wins を、ひらがな数＋ngramスコアで決める
            ind.wins = hira_count/10 + ngram_score
            ind.losses = 50  # 分母用の定数（相対比較できればOK）

        # 進化ステップ
        pop = evolve_one_generation(
            pop,
            population_size=100,
            elite_size=20,
            mutation_rate=0.3,
            next_generation_index=gen + 1,
        )

        print(f"=== Generation {gen+1} ===")
        for ind in pop[:10]:
            print(ind.id, len(ind.text), ind.text[:100])
