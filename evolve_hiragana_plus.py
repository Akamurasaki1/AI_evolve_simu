import random
import string
from dataclasses import dataclass
from typing import List, Dict


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
CHARSET = string.ascii_letters + " 。、「」あいうえおかきくけこさしすせそたちつてとなにぬねのはひふへほまみむめもやゆよらりるれろわをん12341067890!@#$%^&*()-_=+[]{};:'\",.<>?/\\|`~っゃゅょ"


def random_string(min_len: int = 10, max_len: int = 40) -> str:
    length = random.randint(min_len, max_len)
    return "".join(random.choice(CHARSET) for _ in range(length))


def initialize_population(size: int, generation: int = 0) -> List[Individual]:
    population = []
    for i in range(size):
        population.append(Individual(
            id=i,
            text=random_string(),
            generation=generation
        ))
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
        # 全員フィットネス0��ら一様ランダム
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
    return text[:pos] + new_char + text[pos+1:]


def evolve_one_generation(
    population: List[Individual],
    population_size: int,
    elite_size: int,
    mutation_rate: float,
    next_generation_index: int,
) -> List[Individual]:
    # 1. フィットネス計算（wins/losses は事前に埋まっている前提）
    compute_fitness(population)

    # 2. エリート選択
    population_sorted = sorted(population, key=lambda ind: ind.fitness, reverse=True)
    next_pop: List[Individual] = []

    # エリートをそのままコピー
    for i in range(min(elite_size, len(population_sorted))):
        ind = population_sorted[i]
        next_pop.append(Individual(
            id=len(next_pop),
            text=ind.text,
            generation=next_generation_index
        ))

    # 3. 残りを交叉＋変異で埋める
    while len(next_pop) < population_size:
        parent1 = select_parents(population_sorted)
        parent2 = select_parents(population_sorted)
        child_text = crossover(parent1.text, parent2.text)
        child_text = mutate(child_text, mutation_rate=mutation_rate)
        next_pop.append(Individual(
            id=len(next_pop),
            text=child_text,
            generation=next_generation_index
        ))

    return next_pop


if __name__ == "__main__":
    # random.seed(0)

    pop = initialize_population(size=100, generation=0)

    hiragana_set = set("あいうえおかきくけこさしすせそたちつてとなにぬねの"
                       "はひふへほまみむめもやゆよらりるれろわをんっゃゅょ")

    # 特定単語のボーナス設定
    bonus_words = {
        "ねこ": 75,
        "いぬ": 75,
        "ねずみ":75,
        "こんにちは": 110,
        "さようなら": 110,
        "ありがとう": 75,
        "おはよう": 75,
        "こんばんは": 110,
        "すし": 75,
        "てんぷら": 75,
        "さしみ": 75,
        "らーめん":75,
        "うどん": 75,
        "そば": 75,
        "たこやき": 75,
        "おにぎり": 75,
        "やきとり": 75,
        "おちゃ": 75,
        "さけ": 75,
        "みず": 75,
        "ごはん": 75,
        "おかし": 75,
        "くだもの": 75,
        "やさい": 75,
        "にほん": 75,
        "にほん": 75,
        "とうきょう": 75,
        "おおさか": 75,
        "その": 75,
        "これ": 75,
        "あれ": 75,
        "はい": 75,
        "いいえ": 75,
        "すみません": 75,
        "おねがい": 75,
        "いただき": 75,
        "ごちそう": 75,
        "よろしく": 75,
        "さようなら": 75,
        "またね": 75,
        "おやすみ": 75,
        "がんば": 75,
        "おめでとう": 75,
        "します": 75,
        "いただきます": 75,
        "ごちそうさま": 75,
        "ございます": 75,
        "そつろん": 75,
        "けっこん": 75,
        "しゅっせき": 75,
        "かいしゃ": 75,
        "がっこう": 75,
        "ともだち": 75,
        "かぞく": 75,
        "せんせい": 75,
        "がくせい": 75,
        "せいと": 75,
        "ほん": 75,
        "じしょ": 75,
        "ざっし": 75,
        "しんぶん": 75,
        "てがみ": 75,
        "でんわ": 75,
        "です": 75,
        "ます": 75,
        "ですか": 75,
        "でしょう": 75,
        "ください": 75,

        # 必要ならここに追加: "ねずみ": 100 など
    }

    num_generations = 500

    for gen in range(num_generations):
        # ダミー評価：ひらがな数＋単語ボーナスで wins/losses を更新
        for ind in pop:
            text = ind.text

            # ひらがな数
            hira_count = sum(1 for ch in text if ch in hiragana_set)

            # 単語ボーナス
            word_bonus = 0
            for w, b in bonus_words.items():
                if w in text:
                    word_bonus += b

            ind.wins = hira_count + word_bonus
            ind.losses = 20  # 分母用の定数（適当でOK）

        # 進化ステップ
        pop = evolve_one_generation(
            pop,
            population_size=100,
            elite_size=100,
            mutation_rate=0.3,
            next_generation_index=gen + 1,
        )

        print(f"=== Generation {gen+1} ===")
        for ind in pop[:10]:
            print(ind.id, len(ind.text), ind.text[:100])
