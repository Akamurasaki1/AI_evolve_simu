const API_BASE = "http://localhost:8000";  // FastAPI のURL
let currentPair = null;

async function fetchPair() {
    document.getElementById("status").textContent = "ペアを読み込み中...";
    try {
        const res = await fetch(API_BASE + "/pair");
        if (!res.ok) {
            throw new Error("サーバーエラー");
        }
        const data = await res.json();
        currentPair = data;

        document.getElementById("text-a").textContent = data.indiv_a.text;
        document.getElementById("text-b").textContent = data.indiv_b.text;
        document.getElementById("status").textContent =
            "ペアID: " + data.pair_id + "（世代 " + data.generation + "）";
    } catch (e) {
        console.error(e);
        document.getElementById("status").textContent = "ペアの取得に失敗しました";
    }
}

async function sendChoice(chosen) {
    if (!currentPair) return;

    const payload = {
        pair_id: currentPair.pair_id,
        indiv_a_id: currentPair.indiv_a.id,
        indiv_b_id: currentPair.indiv_b.id,
        chosen: chosen   // "A" か "B"
    };

    try {
        const res = await fetch(API_BASE + "/choice", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });
        if (!res.ok) {
            throw new Error("送信エラー");
        }
        // 次のペアを取得
        fetchPair();
    } catch (e) {
        console.error(e);
        document.getElementById("status").textContent = "選択の送信に失敗しました";
    }
}

document.addEventListener("DOMContentLoaded", () => {
    document.getElementById("button-a").addEventListener("click", () => sendChoice("A"));
    document.getElementById("button-b").addEventListener("click", () => sendChoice("B"));
    fetchPair();  // 最初のペアを読み込む
});
