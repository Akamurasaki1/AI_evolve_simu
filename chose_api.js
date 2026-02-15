const API_BASE = "http://localhost:8000";  // FastAPI のURL
let currentPair = null;
let currentGeneration = 0;
let currentEvalCount = 0;
let evalsPerGen = 100;

// Update the status display
function updateStatusDisplay() {
    const statusText = `世代: ${currentGeneration} / 評価回数: ${currentEvalCount} / ${evalsPerGen}`;
    document.getElementById("generation-status").textContent = statusText;
    
    // Show/hide evolve button based on evaluation count
    const evolveButton = document.getElementById("button-evolve");
    if (currentEvalCount >= evalsPerGen) {
        evolveButton.style.display = "inline-block";
    } else {
        evolveButton.style.display = "none";
    }
}

// Fetch status from server
async function fetchStatus() {
    try {
        const res = await fetch(API_BASE + "/status");
        if (!res.ok) {
            throw new Error("サーバーエラー");
        }
        const data = await res.json();
        currentGeneration = data.generation;
        currentEvalCount = data.eval_count;
        evalsPerGen = data.evals_per_gen;
        updateStatusDisplay();
    } catch (e) {
        console.error(e);
        document.getElementById("status").textContent = "ステータスの取得に失敗しました";
    }
}

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
        const data = await res.json();
        
        // Update local state from response
        currentGeneration = data.generation;
        currentEvalCount = data.eval_count;
        evalsPerGen = data.evals_per_gen;
        updateStatusDisplay();
        
        // 次のペアを取得
        fetchPair();
    } catch (e) {
        console.error(e);
        document.getElementById("status").textContent = "選択の送信に失敗しました";
    }
}

async function evolveGeneration() {
    document.getElementById("status").textContent = "世代を進化中...";
    try {
        const res = await fetch(API_BASE + "/evolve", {
            method: "POST",
            headers: { "Content-Type": "application/json" }
        });
        if (!res.ok) {
            throw new Error("進化エラー");
        }
        const data = await res.json();
        
        // Update status from response
        currentGeneration = data.new_generation;
        currentEvalCount = 0;
        updateStatusDisplay();
        
        document.getElementById("status").textContent = 
            `世代 ${data.old_generation} → ${data.new_generation} に進化しました！`;
        
        // Fetch a new pair from the new generation
        fetchPair();
    } catch (e) {
        console.error(e);
        document.getElementById("status").textContent = "進化に失敗しました";
    }
}

document.addEventListener("DOMContentLoaded", () => {
    document.getElementById("button-a").addEventListener("click", () => sendChoice("A"));
    document.getElementById("button-b").addEventListener("click", () => sendChoice("B"));
    document.getElementById("button-fetch").addEventListener("click", fetchPair);
    document.getElementById("button-evolve").addEventListener("click", evolveGeneration);
    
    // Initialize status on page load
    fetchStatus();
});
