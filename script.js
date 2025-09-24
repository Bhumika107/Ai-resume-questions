const uploadForm = document.getElementById("uploadForm");
const resumeFile = document.getElementById("resumeFile");
const resumeTextContainer = document.getElementById("resumeTextContainer");
const resumeText = document.getElementById("resumeText");
const generateBtn = document.getElementById("generateBtn");
const questionsContainer = document.getElementById("questionsContainer");
const questionsList = document.getElementById("questionsList");
const downloadBtn = document.getElementById("downloadBtn");

let extractedText = "";
let generatedQuestions = "";

// Handle PDF upload
uploadForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const file = resumeFile.files[0];
    if (!file) return alert("Please upload a PDF file");

    const formData = new FormData();
    formData.append("file", file);

    const response = await fetch("/extract-text", {
        method: "POST",
        body: formData,
    });

    const data = await response.json();
    if (data.text) {
        extractedText = data.text;
        resumeText.textContent = extractedText;
        resumeTextContainer.classList.remove("hidden");
    } else {
        alert("Error extracting text");
    }
});

// Generate questions
generateBtn.addEventListener("click", async () => {
    const response = await fetch("/generate-questions", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ resume_text: extractedText }),
    });

    const data = await response.json();
    if (data.questions) {
        generatedQuestions = data.questions.split("\n");
        questionsList.innerHTML = "";
        generatedQuestions.forEach((q) => {
            if (q.trim()) {
                const li = document.createElement("li");
                li.textContent = q;
                questionsList.appendChild(li);
            }
        });
        questionsContainer.classList.remove("hidden");
    } else {
        alert("Error generating questions");
    }
});

// Download PDF
downloadBtn.addEventListener("click", () => {
    const { jsPDF } = window.jspdf;
    const doc = new jsPDF();
    doc.text("Generated Interview Questions", 10, 10);
    let y = 20;
    generatedQuestions.forEach((q, i) => {
        doc.text(`${i + 1}. ${q}`, 10, y);
        y += 10;
    });
    doc.save("interview_questions.pdf");
});
