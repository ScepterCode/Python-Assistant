<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DataSage: AI Python/DS Expert Agent</title>
    <!-- Load Tailwind CSS -->
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        /* Custom styles for better readability and aesthetics */
        body {
            font-family: 'Inter', sans-serif;
            background-color: #f7fafc; /* Light gray background */
        }
        .container-card {
            max-width: 900px;
            margin: 2rem auto;
            padding: 2rem;
            background-color: #ffffff;
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 0 10px -5px rgba(0, 0, 0, 0.04);
            border-radius: 1rem;
        }
        #output-area {
            min-height: 200px;
            white-space: pre-wrap;
            word-wrap: break-word;
        }
        /* Style for Markdown code blocks inside the output */
        #output-area pre {
            background-color: #e2e8f0;
            padding: 1rem;
            border-radius: 0.5rem;
            overflow-x: auto;
            margin-top: 1rem;
            margin-bottom: 1rem;
            font-family: monospace;
            border: 1px solid #cbd5e1;
        }
        /* Style for Markdown lists and bold text */
        #output-area ul, #output-area ol {
            margin-left: 1.5rem;
            list-style-type: disc;
        }
        #output-area h2 {
            font-size: 1.5rem;
            font-weight: 700;
            margin-top: 1.5rem;
            margin-bottom: 0.5rem;
        }
        #output-area h3 {
            font-size: 1.25rem;
            font-weight: 600;
            margin-top: 1rem;
            margin-bottom: 0.5rem;
            color: #1a202c;
        }
        .citation-link {
            text-decoration: underline;
            color: #4299e1; /* Blue for links */
        }
    </style>
</head>
<body>

    <div class="container-card">
        <h1 class="text-4xl font-bold text-center text-gray-800 mb-2">🤖 DataSage: AI Python/DS Expert</h1>
        <p class="text-center text-gray-500 mb-8">Ask any question about Python, Data Science, or Machine Learning.</p>

        <!-- Input Area -->
        <div class="mb-6">
            <textarea id="prompt-input" rows="4" class="w-full p-4 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500 transition duration-150 ease-in-out" placeholder="E.g., How do I handle missing values in a Pandas DataFrame using imputation methods?"></textarea>
        </div>
        
        <button id="submit-btn" onclick="askPythonQuestion()" class="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-3 px-4 rounded-lg transition duration-150 ease-in-out shadow-md disabled:opacity-50 flex items-center justify-center">
            <span id="btn-text">Get Expert Answer</span>
            <svg id="loading-spinner" class="animate-spin -ml-1 mr-3 h-5 w-5 text-white hidden" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
        </button>

        <!-- Output Area -->
        <div class="mt-8">
            <h2 class="text-2xl font-semibold text-gray-700 mb-4">DataSage's Response:</h2>
            <div id="output-container" class="border border-gray-200 p-6 rounded-lg bg-gray-50">
                <p id="output-area" class="text-gray-700 leading-relaxed">Your expert answers will appear here.</p>
                <div id="citation-area" class="mt-4 text-sm text-gray-500 border-t pt-3 hidden">
                    <p class="font-semibold mb-1">Sources:</p>
                    <ul id="citation-list" class="list-none p-0 m-0 space-y-1"></ul>
                </div>
            </div>
        </div>

        <!-- Error/Message Box -->
        <div id="message-box" class="mt-4 p-4 text-sm rounded-lg hidden" role="alert"></div>
    </div>

    <script>
        // Set up the API key and base URL. The Canvas environment provides the key automatically
        // when the apiKey is an empty string.
        const apiKey = ""; 
        const apiUrl = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-05-20:generateContent";

        // UI Element References
        const promptInput = document.getElementById('prompt-input');
        const submitBtn = document.getElementById('submit-btn');
        const btnText = document.getElementById('btn-text');
        const loadingSpinner = document.getElementById('loading-spinner');
        const outputArea = document.getElementById('output-area');
        const citationArea = document.getElementById('citation-area');
        const citationList = document.getElementById('citation-list');
        const messageBox = document.getElementById('message-box');

        /**
         * Helper function to show messages (errors or info)
         * @param {string} message - The message content
         * @param {string} type - 'success', 'error', or 'info'
         */
        function showMessage(message, type = 'info') {
            messageBox.textContent = message;
            messageBox.classList.remove('hidden', 'bg-red-100', 'text-red-700', 'bg-green-100', 'text-green-700', 'bg-blue-100', 'text-blue-700');
            
            if (type === 'error') {
                messageBox.classList.add('bg-red-100', 'text-red-700');
            } else if (type === 'success') {
                messageBox.classList.add('bg-green-100', 'text-green-700');
            } else {
                messageBox.classList.add('bg-blue-100', 'text-blue-700');
            }
        }

        /**
         * Parses Markdown text into HTML for display in the output area.
         * This is a simplified parser suitable for basic markdown (headers, lists, code blocks).
         * @param {string} markdownText - The text in Markdown format.
         * @returns {string} The text converted to HTML.
         */
        function markdownToHtml(markdownText) {
            // Convert code blocks (triple backticks)
            markdownText = markdownText.replace(/```(\w+)?\n([\s\S]*?)```/g, (match, p1, p2) => {
                const language = p1 ? `lang-${p1}` : 'lang-plain';
                // Escape HTML characters inside code blocks
                const escapedCode = p2.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
                return `<pre><code class="${language}">${escapedCode}</code></pre>`;
            });

            // Convert headers (h2 and h3)
            markdownText = markdownText.replace(/^### (.*$)/gim, '<h3>$1</h3>');
            markdownText = markdownText.replace(/^## (.*$)/gim, '<h2>$1</h2>');
            markdownText = markdownText.replace(/^# (.*$)/gim, '<h1>$1</h1>');

            // Convert lists
            markdownText = markdownText.replace(/^\* (.*$)/gim, '<li>$1</li>');
            markdownText = markdownText.replace(/^\- (.*$)/gim, '<li>$1</li>');
            markdownText = markdownText.replace(/(<li>.*<\/li>)/gms, '<ul>$1</ul>');
            
            // Remove paragraph tags around ul/ol
            markdownText = markdownText.replace(/<p><ul>/g, '<ul>').replace(/<\/ul><\/p>/g, '</ul>');

            // Convert bold text
            markdownText = markdownText.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
            
            // Convert remaining new lines to <br> for simple paragraphs
            markdownText = markdownText.replace(/\n\n/g, '</p><p>').replace(/\n/g, '<br>');

            // Wrap in an initial paragraph tag if necessary
            if (!markdownText.startsWith('<')) {
                markdownText = `<p>${markdownText}</p>`;
            }

            return markdownText;
        }

        /**
         * General-purpose fetch wrapper with exponential backoff.
         * @param {string} url - The URL to fetch.
         * @param {object} options - Fetch request options.
         * @param {number} maxRetries - Maximum number of retries.
         * @returns {Promise<Response>} The fetch response object.
         */
        async function fetchWithExponentialBackoff(url, options, maxRetries = 5) {
            for (let i = 0; i < maxRetries; i++) {
                try {
                    const response = await fetch(url, options);
                    if (response.status !== 429) { // Not a rate limit error, proceed
                        return response;
                    }
                    // Handle 429 (Too Many Requests) - Retry with delay
                    const delay = Math.pow(2, i) * 1000 + Math.random() * 1000;
                    await new Promise(resolve => setTimeout(resolve, delay));
                } catch (error) {
                    // Handle network errors - Retry with delay
                    const delay = Math.pow(2, i) * 1000 + Math.random() * 1000;
                    await new Promise(resolve => setTimeout(resolve, delay));
                }
            }
            throw new Error("API request failed after multiple retries.");
        }


        /**
         * Main function to call the Gemini API and get the answer.
         */
        async function askPythonQuestion() {
            const userQuery = promptInput.value.trim();
            if (!userQuery) {
                showMessage("Please enter a Python or Data Science question.", 'info');
                return;
            }

            // Reset UI state
            messageBox.classList.add('hidden');
            outputArea.innerHTML = '<p class="text-indigo-500">Generating expert response...</p>';
            citationArea.classList.add('hidden');
            citationList.innerHTML = '';
            submitBtn.disabled = true;
            btnText.textContent = "Processing...";
            loadingSpinner.classList.remove('hidden');

            const systemPrompt = "You are 'DataSage', an expert Python and Data Science/Machine Learning tutor. Your goal is to provide accurate, comprehensive, and clear answers to all Python, Data Science, and Machine Learning related questions. Always include relevant, well-commented code examples when explaining concepts or commands. Format your response using clear Markdown, focusing on readability and technical depth.";

            const payload = {
                contents: [{ parts: [{ text: userQuery }] }],
                // Use Google Search grounding to ensure answers are up-to-date
                tools: [{ "google_search": {} }],
                systemInstruction: {
                    parts: [{ text: systemPrompt }]
                }
            };

            const fullUrl = `${apiUrl}?key=${apiKey}`;

            try {
                const response = await fetchWithExponentialBackoff(fullUrl, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                
                if (!response.ok) {
                    const errorJson = await response.json();
                    throw new Error(`API Error: ${response.status} - ${errorJson.error?.message || 'Unknown error'}`);
                }


                const result = await response.json();
                const candidate = result.candidates?.[0];

                if (candidate && candidate.content?.parts?.[0]?.text) {
                    // 1. Extract and format the generated text
                    const text = candidate.content.parts[0].text;
                    outputArea.innerHTML = markdownToHtml(text);
                    
                    // 2. Extract and display grounding sources (citations)
                    let sources = [];
                    const groundingMetadata = candidate.groundingMetadata;
                    if (groundingMetadata && groundingMetadata.groundingAttributions) {
                        sources = groundingMetadata.groundingAttributions
                            .map(attribution => ({
                                uri: attribution.web?.uri,
                                title: attribution.web?.title,
                            }))
                            .filter(source => source.uri && source.title);
                    }

                    if (sources.length > 0) {
                        sources.forEach((source, index) => {
                            const li = document.createElement('li');
                            li.innerHTML = `<a href="${source.uri}" target="_blank" class="citation-link hover:text-indigo-600 transition duration-150 ease-in-out">
                                ${index + 1}. ${source.title || source.uri}
                            </a>`;
                            citationList.appendChild(li);
                        });
                        citationArea.classList.remove('hidden');
                    } else {
                        citationArea.classList.add('hidden');
                    }

                    showMessage("Answer generated successfully!", 'success');

                } else {
                    throw new Error("The API returned an invalid response structure or no text content.");
                }

            } catch (error) {
                console.error("Gemini API call failed:", error);
                outputArea.innerHTML = '<p class="text-red-500">Sorry, DataSage encountered an error.</p>';
                showMessage(`Error: ${error.message}`, 'error');

            } finally {
                // Restore UI state
                submitBtn.disabled = false;
                btnText.textContent = "Get Expert Answer";
                loadingSpinner.classList.add('hidden');
            }
        }
    </script>

</body>
</html>
