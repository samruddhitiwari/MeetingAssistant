import PySimpleGUI as sg
import subprocess, os
from modules.transcribe import transcribe
from modules.summarize  import summarize
from modules.search import build_faiss_index, query_faiss
from modules.query_parser import extract_keywords
import openai
openai.api_key = 'openai-api-key'
def generate_answer_with_llm(query, context):
    """
    Generates an answer from the LLM (e.g., GPT-3) based on the retrieved context.
    """
    prompt = f"Question: {query}\n\nContext: {context}\n\nAnswer:"
    try:
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=150,
            temperature=0.7
        )
        answer = response.choices[0].text.strip()
        return answer
    except Exception as e:
        return f"[ERROR] LLM failed: {e}"





# 1️⃣ Define the window layout
layout = [
    [sg.Text("Meeting Assistant")],
    [sg.Input(key="-FILE-"), sg.FileBrowse(file_types=(("Audio/Video", "*.wav;*.mp4"), ("All", "*.*")))],
    [sg.Button("Process"), sg.Button("Search Index"), sg.Exit()],
    [sg.Text("Query:"), sg.Input(key="-SEARCH-"), sg.Button("Search")],
    [sg.Multiline(size=(70, 10), key="-RESULTS-")],
]

# 2️⃣ Create the window
window = sg.Window("23 Ventures Assistant", layout)

while True:
    try:
        event, values = window.read()
    except Exception as e:
        sg.popup_error(f"GUI Error: {e}")
        continue  # This continue should only be inside the except block

    if event in (sg.WIN_CLOSED, "Exit"):
        break

    if event == "Search":
        query_text = values["-SEARCH-"].strip()
        if not query_text:
            sg.popup("Please enter a search query.")
            continue

        # Step 1: Parse the query for keywords (dates, actions, topics)
        sg.popup("Parsing query...")
        keywords = extract_keywords(query_text)

        # Display parsed keywords
        date_text = ", ".join(keywords["dates"]) if keywords["dates"] else "No date found."
        action_text = ", ".join(keywords["actions"]) if keywords["actions"] else "No actions found."
        topic_text = ", ".join(keywords["topics"]) if keywords["topics"] else "No topics found."

        result_text = f"Dates: {date_text}\nActions: {action_text}\nTopics: {topic_text}"
        window["-RESULTS-"].update(result_text)

        # Step 2: Perform FAISS search
        sg.popup("Searching…")
        results = query_faiss(query_text, k=5)
        if not results:
            window["-RESULTS-"].update("No matching meetings found.")
        else:
            context = "\n".join([r['content'] for r in results[:3]])  
            sg.popup("Generating answer...")
            answer = generate_answer_with_llm(query_text, context)
            window["-RESULTS-"].update(answer)

    if event == "Process":
        try:
            raw_path = values["-FILE-"]
            if not raw_path:
                sg.popup("Please select a file first.")
                continue

            from datetime import date
            from pathlib import Path
            today = date.today()
            slug = Path(raw_path).stem
            base = Path("meetings")/f"{today.year}"/f"{today:%m}"/f"{today:%d}-{slug}"
            raw_dst = base/Path(raw_path).name
            txt = base/"transcript.txt"
            summ = base/"summary.txt"
            os.makedirs(base, exist_ok=True)

            sg.popup("Copying file…")
            subprocess.run(["cp", raw_path, str(raw_dst)])

            sg.popup("Transcribing…")
            transcribe(str(raw_dst), str(txt))

            sg.popup("Summarizing…")
            summarize(str(txt), str(summ))

            sg.popup("Updating search index…")
            build_faiss_index()

            sg.popup(f"Done!\nTranscript: {txt}\nSummary: {summ}")
        except Exception as e:
            sg.popup_error(f"[ERROR] Processing failed: {e}")

    if event == "Refresh All Indexes":
        sg.popup("Refreshing all FAISS indexes…")
        build_faiss_index()
        sg.popup("All indexes have been refreshed.")

window.close()

