// ============================================================
// AI RESUME SCREENING & SKILLS GAP ANALYSIS
// SCRIPT.JS
// ============================================================


// ============================================================
// ANALYZE RESUME
// ============================================================

async function analyzeResume() {

    const fileInput = document.getElementById("resumeFile");
    const result = document.getElementById("result");
    const progressBar = document.getElementById("progressBar");

    // --------------------------------------------------------
    // CHECK REQUIRED ELEMENTS
    // --------------------------------------------------------

    if (!fileInput) {
        console.error("resumeFile element not found.");
        return;
    }

    if (!result) {
        console.error("result element not found.");
        return;
    }


    // --------------------------------------------------------
    // CHECK FILE
    // --------------------------------------------------------

    if (!fileInput.files || fileInput.files.length === 0) {

        result.innerHTML =
            "❌ Please upload a resume first.";

        result.style.color = "red";

        return;
    }


    const file = fileInput.files[0];

    const fileName = file.name;


    // --------------------------------------------------------
    // CHECK FILE TYPE
    // --------------------------------------------------------

    const allowedExtensions = [
        ".pdf",
        ".docx"
    ];

    const lowerFileName =
        fileName.toLowerCase();

    const validFile =
        allowedExtensions.some(
            extension =>
                lowerFileName.endsWith(extension)
        );


    if (!validFile) {

        result.innerHTML =
            "❌ Please upload a PDF or DOCX resume.";

        result.style.color = "red";

        return;
    }


    // --------------------------------------------------------
    // SHOW SELECTED FILE
    // --------------------------------------------------------

    const previewName =
        document.getElementById("previewName");

    if (previewName) {

        previewName.innerHTML =
            "📄 Selected File: " + fileName;
    }


    const previewNameCard =
        document.getElementById("previewNameCard");

    if (previewNameCard) {

        previewNameCard.innerHTML =
            fileName;
    }


    // --------------------------------------------------------
    // CREATE FORM DATA
    // --------------------------------------------------------

    const formData = new FormData();

    formData.append(
        "resume",
        file
    );


    // --------------------------------------------------------
    // SHOW LOADING MESSAGE
    // --------------------------------------------------------

    result.innerHTML =
        "⏳ Analyzing your resume...";

    result.style.color =
        "white";


    // --------------------------------------------------------
    // SHOW PROGRESS BAR
    // --------------------------------------------------------

    const progressContainer =
        document.querySelector(
            ".progress-container"
        );


    if (progressContainer) {

        progressContainer.style.display =
            "block";
    }


    if (progressBar) {

        progressBar.style.width =
            "10%";
    }


    // --------------------------------------------------------
    // ANALYSIS REQUEST
    // --------------------------------------------------------

    try {

        console.log(
            "================================"
        );

        console.log(
            "Starting Resume Analysis"
        );

        console.log(
            "File:",
            fileName
        );

        console.log(
            "File Type:",
            file.type
        );

        console.log(
            "File Size:",
            file.size
        );

        console.log(
            "================================"
        );


        // ----------------------------------------------------
        // SEND FILE TO FLASK
        // ----------------------------------------------------

        const response = await fetch(
            "/analyze",
            {
                method: "POST",
                body: formData
            }
        );


        console.log(
            "HTTP STATUS:",
            response.status
        );

        console.log(
            "HTTP STATUS TEXT:",
            response.statusText
        );


        // ----------------------------------------------------
        // READ RESPONSE AS TEXT FIRST
        // ----------------------------------------------------
        // This prevents:
        // Unexpected end of JSON input
        // ----------------------------------------------------

        const responseText =
            await response.text();


        console.log(
            "SERVER RESPONSE:",
            responseText
        );


        // ----------------------------------------------------
        // EMPTY RESPONSE CHECK
        // ----------------------------------------------------

        if (!responseText.trim()) {

            throw new Error(
                "Server returned an empty response. HTTP Status: " +
                response.status
            );
        }


        // ----------------------------------------------------
        // PARSE JSON SAFELY
        // ----------------------------------------------------

        let data;

        try {

            data =
                JSON.parse(responseText);

        } catch (jsonError) {

            console.error(
                "JSON PARSE ERROR:",
                jsonError
            );

            throw new Error(
                "Server returned invalid JSON: " +
                responseText.substring(0, 300)
            );
        }


        console.log(
            "PARSED DATA:",
            data
        );


        // ----------------------------------------------------
        // HANDLE SERVER ERROR
        // ----------------------------------------------------

        if (!response.ok) {

            throw new Error(
                data.details ||
                data.error ||
                data.message ||
                "Server returned HTTP " +
                response.status
            );
        }


        // ----------------------------------------------------
        // HANDLE BACKEND FAILURE
        // ----------------------------------------------------

        if (data.success === false) {

            throw new Error(
                data.details ||
                data.error ||
                data.message ||
                "Resume analysis failed."
            );
        }


        // ----------------------------------------------------
        // ATS SCORE
        // ----------------------------------------------------

        const score =
            Number(data.ats_score) || 0;


        // ----------------------------------------------------
        // DOMAIN
        // ----------------------------------------------------

        const domainElement =
            document.getElementById(
                "domain"
            );


        if (domainElement) {

            domainElement.innerHTML =
                data.domain ||
                "General";
        }


        // ----------------------------------------------------
        // MISSING SKILLS
        // ----------------------------------------------------

        const missingSkillsElement =
            document.getElementById(
                "missingSkills"
            );


        if (missingSkillsElement) {

            const missingSkills =
                Array.isArray(
                    data.missing_skills
                )
                    ? data.missing_skills
                    : [];


            if (
                missingSkills.length > 0
            ) {

                missingSkillsElement.innerHTML =
                    missingSkills.join(", ");

            } else {

                missingSkillsElement.innerHTML =
                    "No major skill gaps detected";
            }
        }


        // ----------------------------------------------------
        // ATS SCORE CIRCLE
        // ----------------------------------------------------

        const circleScore =
            document.getElementById(
                "circleScore"
            );


        if (circleScore) {

            circleScore.innerHTML =
                score + "%";
        }


        // ----------------------------------------------------
        // RESUME STRENGTH
        // ----------------------------------------------------

        const strengthText =
            document.getElementById(
                "strengthText"
            );


        if (strengthText) {

            strengthText.innerHTML =
                data.strength ||
                "Not available";
        }


        // ----------------------------------------------------
        // SKILLS
        // ----------------------------------------------------

        const skillsList =
            document.getElementById(
                "skillsList"
            );


        if (skillsList) {

            const skills =
                Array.isArray(
                    data.skills
                )
                    ? data.skills
                    : [];


            if (skills.length > 0) {

                skillsList.innerHTML =
                    skills.join(", ");

            } else {

                skillsList.innerHTML =
                    "No skills detected";
            }
        }


        // ----------------------------------------------------
        // RECOMMENDATIONS
        // ----------------------------------------------------

        const recommendationsElement =
            document.getElementById(
                "recommendations"
            );


        if (recommendationsElement) {

            const recommendations =
                Array.isArray(
                    data.recommendations
                )
                    ? data.recommendations
                    : [];


            if (
                recommendations.length > 0
            ) {

                recommendationsElement.innerHTML =
                    recommendations.join("<br>");

            } else {

                recommendationsElement.innerHTML =
                    "No recommendations available";
            }
        }


        // ----------------------------------------------------
        // PROGRESS BAR
        // ----------------------------------------------------

        if (progressBar) {

            progressBar.style.width =
                score + "%";


            if (score >= 90) {

                progressBar.style.background =
                    "limegreen";

            }

            else if (score >= 75) {

                progressBar.style.background =
                    "gold";

            }

            else {

                progressBar.style.background =
                    "red";
            }
        }


        // ----------------------------------------------------
        // SUCCESS MESSAGE
        // ----------------------------------------------------

        result.innerHTML = `

            <div style="
                font-size: 18px;
                font-weight: bold;
                margin-bottom: 15px;
            ">
                ✅ Resume Analyzed Successfully!
            </div>

            <div>
                📄 File Name:
                ${data.filename || fileName}
            </div>

            <div>
                ⭐ ATS Score:
                ${score}/100
            </div>

            <div>
                🎯 Domain:
                ${data.domain || "General"}
            </div>

            <div>
                💪 Resume Strength:
                ${data.strength || "Not available"}
            </div>

        `;


        result.style.color =
            "lightgreen";


        // ----------------------------------------------------
        // FINISHED
        // ----------------------------------------------------

        console.log(
            "================================"
        );

        console.log(
            "Resume Analysis Completed"
        );

        console.log(
            "ATS Score:",
            score
        );

        console.log(
            "Domain:",
            data.domain
        );

        console.log(
            "Skills:",
            data.skills
        );

        console.log(
            "Missing Skills:",
            data.missing_skills
        );

        console.log(
            "================================"
        );
    }


    // ========================================================
    // ERROR HANDLING
    // ========================================================

    catch (error) {

        console.error(
            "================================"
        );

        console.error(
            "RESUME ANALYSIS ERROR"
        );

        console.error(
            error
        );

        console.error(
            "================================"
        );


        result.innerHTML = `

            <div style="
                font-size: 18px;
                font-weight: bold;
                margin-bottom: 15px;
            ">
                ❌ Resume Analysis Failed.
            </div>

            <div style="
                font-size: 15px;
                word-break: break-word;
            ">
                ${error.message}
            </div>

        `;


        result.style.color =
            "red";
    }
}



// ============================================================
// DARK / LIGHT THEME
// ============================================================

function toggleTheme() {

    document.body.classList.toggle(
        "dark-mode"
    );
}



// ============================================================
// RESUME FILE INPUT
// ============================================================

const fileInput =
    document.getElementById(
        "resumeFile"
    );


if (fileInput) {

    fileInput.addEventListener(
        "change",
        function () {

            if (
                !this.files ||
                this.files.length === 0
            ) {

                return;
            }


            const selectedFile =
                this.files[0];


            const fileName =
                selectedFile.name;


            // -----------------------------------------------
            // SHOW FILE NAME
            // -----------------------------------------------

            const previewName =
                document.getElementById(
                    "previewName"
                );


            if (previewName) {

                previewName.innerHTML =
                    "📄 Selected File: " +
                    fileName;
            }


            const previewNameCard =
                document.getElementById(
                    "previewNameCard"
                );


            if (previewNameCard) {

                previewNameCard.innerHTML =
                    fileName;
            }


            // -----------------------------------------------
            // RESET RESULT
            // -----------------------------------------------

            const result =
                document.getElementById(
                    "result"
                );


            if (result) {

                result.innerHTML =
                    "📄 Resume selected. Click Analyze Resume.";

                result.style.color =
                    "white";
            }


            // -----------------------------------------------
            // RESET PROGRESS
            // -----------------------------------------------

            const progressBar =
                document.getElementById(
                    "progressBar"
                );


            if (progressBar) {

                progressBar.style.width =
                    "0%";
            }


            console.log(
                "Selected Resume:",
                fileName
            );
        }
    );
}



// ============================================================
// DOWNLOAD REPORT
// ============================================================

function downloadReport() {

    window.open(
        "/download-report",
        "_blank"
    );
}



// ============================================================
// PAGE LOAD
// ============================================================

document.addEventListener(
    "DOMContentLoaded",
    function () {

        console.log(
            "AI Resume Analyzer loaded successfully."
        );


        // ----------------------------------------------------
        // CHECK ANALYZE BUTTON
        // ----------------------------------------------------

        const analyzeButton =
            document.querySelector(
                "button[onclick*='analyzeResume']"
            );


        if (analyzeButton) {

            console.log(
                "Analyze button detected."
            );

        } else {

            console.warn(
                "Analyze button not detected."
            );
        }


        // ----------------------------------------------------
        // CHECK FILE INPUT
        // ----------------------------------------------------

        const resumeInput =
            document.getElementById(
                "resumeFile"
            );


        if (resumeInput) {

            console.log(
                "Resume input detected."
            );

        } else {

            console.warn(
                "Resume input not detected."
            );
        }
    }
);