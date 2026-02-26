async function runQuery() {
    const question = document.getElementById("questionInput").value;
    const resultSection = document.getElementById("resultSection");
    const loading = document.getElementById("loading");

    resultSection.innerHTML = "";
    loading.classList.remove("hidden");

    try {
        const response = await fetch(`http://127.0.0.1:8000/query?query=${encodeURIComponent(question)}`, {
            method: "POST"
        });

        const data = await response.json();
        loading.classList.add("hidden");

        renderResult(data.result);

    } catch (error) {
        loading.classList.add("hidden");
        resultSection.innerHTML = "<p>Error occurred</p>";
        console.error(error);
    }
}

function renderResult(result) {
    const resultSection = document.getElementById("resultSection");

    if (!result) {
        resultSection.innerHTML = "<p>No result</p>";
        return;
    }

    // If result is number
    if (typeof result === "number") {
        resultSection.innerHTML = `<h2>${result}</h2>`;
        return;
    }

    // If result is list
    if (Array.isArray(result)) {
        if (result.length === 0) {
            resultSection.innerHTML = "<p>No data found</p>";
            return;
        }

        const table = document.createElement("table");
        const headerRow = document.createElement("tr");

        Object.keys(result[0]).forEach(key => {
            const th = document.createElement("th");
            th.textContent = key;
            headerRow.appendChild(th);
        });

        table.appendChild(headerRow);

        result.forEach(row => {
            const tr = document.createElement("tr");
            Object.values(row).forEach(value => {
                const td = document.createElement("td");
                td.textContent = value;
                tr.appendChild(td);
            });
            table.appendChild(tr);
        });

        resultSection.appendChild(table);
    }
}