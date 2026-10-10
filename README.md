# Offline AI Document Generator

A command line tool that turns a plain sentence like "Create a project report for an AI based attendance system" into finished documents. The writing is done by a language model running on your own computer through Ollama, so it works without internet and without any API key.

From one prompt it can create Word, PDF, PowerPoint and Excel files, plus ten other formats listed below.

This project was made for an inter college hackathon. The problem statement asked for an AI application that converts natural language requirements into Word, PDF, PowerPoint and Excel documents, with the AI model running locally and no external AI APIs.

---

## Before you start: install Ollama

This project does not work without Ollama. Please install it first.

1. Download Ollama from https://ollama.com and install it.
2. Open a terminal and check that it works:

```
ollama --version
```

3. Download a model (the default one is small and fast):

```
ollama pull qwen2.5:3b
```

You need internet for these steps and for installing the Python packages. After that, everything runs offline.

Not sure which model suits your computer? See [Choosing a model for your computer](#choosing-a-model-for-your-computer) below.

---

## Supported formats

| Format | Made with | What you get |
|---|---|---|
| .docx | python-docx | Cover page, numbered headings, bullet points, tables |
| .doc | plain RTF | Same content in the older Word format |
| .odt | odfpy | OpenDocument text for LibreOffice Writer |
| .pdf | ReportLab | Cover page, tables, page numbers |
| .pptx | python-pptx | Title slide, one slide per section, table slides |
| .xlsx | openpyxl | Overview sheet, one sheet per table, a bar chart when the data is numeric |
| .csv | csv module | Section overview followed by each table |
| .html | plain Python | One self contained web page, works without internet |
| .json | Pydantic | The full document as structured data |
| .xml | ElementTree | The same structure as XML |
| .py | plain Python | A script that holds the document as data and prints it when run |
| .ipynb | plain Python | A Jupyter notebook with text cells and table cells |
| .log | plain Python | A timestamped log, with a warning for any section that failed |
| .zip | zipfile | All the other generated files in one bundle |

The `.doc` file is really RTF saved with a `.doc` extension. Microsoft Word opens it like a normal Word file, but Python cannot write the true binary `.doc` format on its own.

---

## How it works

```
Your prompt
   |
Stage 1: the model writes a title and a list of section headings
   |
Stage 2: the model writes each section one at a time
   |
One validated Document object (Pydantic)
   |
Renderers: docx, doc, odt, pdf, pptx, xlsx, csv, html, json, xml, py, ipynb, log
   |
Optional zip bundle
```

Small models struggle with one big request but do much better with small ones, so the document is written section by section. The model is forced to answer in a fixed JSON shape, and the answer is checked before it is used. If a reply is invalid, the program asks again up to three times. If a section still fails, a placeholder is used so the rest of the document is still produced.

All formats are created from the same Document object, so the content is identical in every file.

```python
class Table:    headers, rows
class Section:  heading, paragraphs, bullets, table (optional)
class Document: title, subtitle, sections
```

A section becomes a heading in Word and PDF, one slide in PowerPoint, and, if it has a table, one sheet in Excel.

---

## Project structure

```
docgen/
├── README.md
├── requirements.txt
├── schema.py              Data models
├── llm.py                 Talks to Ollama, validates output, retries
├── test_run.py            Main tool: prompt in, documents out
├── test_render_only.py    Creates and checks every format, no AI needed
├── check_system.py        Checks your PC and suggests a model
└── renderers/
    ├── __init__.py        Format registry and zip bundler
    ├── docx_r.py   doc_r.py   odt_r.py   pdf_r.py
    ├── pptx_r.py   xlsx_r.py  csv_r.py   html_r.py
    └── json_r.py   xml_r.py   py_r.py    ipynb_r.py   log_r.py
```

---

## Installation

You need Python 3.9 or newer and Ollama (see above).

```
git clone https://github.com/<your-username>/<your-repo>.git
cd <your-repo>/docgen
```

Windows (PowerShell):

```
python -m venv venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
venv\Scripts\activate
pip install -r requirements.txt
```

macOS or Linux:

```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

When the virtual environment is active, your prompt starts with `(venv)`. Check the install without using the AI:

```
python test_render_only.py
```

It should end with `All 14 formats valid.`

---

## Choosing a model for your computer

The model decides how good the writing is, and your computer decides which models you can run. I built this on a laptop with modest specs, so the default model (`qwen2.5:3b`) is a small one. If your computer is stronger, you should use a bigger model. The results are noticeably better.

### Step 1: find out your specs

Run the included checker:

```
python check_system.py
```

It shows your RAM, CPU cores and NVIDIA GPU (if any), then suggests a model and prints the commands to use it. You can also check by hand:

| System | How to check |
|---|---|
| Windows | Task Manager, Performance tab. Look at Memory and GPU (Dedicated GPU memory) |
| macOS | Apple menu, About This Mac |
| Linux | `free -h` and `nvidia-smi` |

### Step 2: pick a model

| Total RAM | Model | Download size (approx.) | What to expect |
|---|---|---|---|
| Under 6 GB | qwen2.5:1.5b | 1 GB | Fast, but the writing is weak |
| 6 to 11 GB | qwen2.5:3b | 2 GB | Default. Decent for short documents |
| 12 to 23 GB | qwen2.5:7b or llama3.1:8b | 5 GB | Better writing and fewer failed sections |
| 24 to 47 GB | qwen2.5:14b | 9 GB | Strong, but slow without a GPU |
| 48 GB or more | qwen2.5:32b | 20 GB | Best quality in this list |

These are rough guides, not exact limits. Leave a few GB free for your operating system and other programs. A graphics card with enough memory makes everything much faster. If the model does not fit in GPU memory, Ollama uses system RAM for the rest, which works but is slower. You can browse every available model at https://ollama.com/library.

### Step 3: download and use it

```
ollama pull qwen2.5:7b
python test_run.py "Create a project report for an attendance system" --model qwen2.5:7b
```

To make a model your default for the whole terminal session instead of typing `--model` each time:

```
$env:DOCGEN_MODEL = "qwen2.5:7b"        (Windows PowerShell)
export DOCGEN_MODEL=qwen2.5:7b          (macOS or Linux)
```

Or change the `MODEL` line near the top of `llm.py`.

---

## Usage

```
python test_run.py "<your prompt>" [options]
```

| Option | Default | Meaning |
|---|---|---|
| --formats | all | Which files to create, for example `docx,pdf,xlsx` |
| --name | report | File name without the extension |
| --type | Project Report | Kind of document, which guides the writing |
| --sections | 6 | Number of sections (this is also the number of slides) |
| --model | qwen2.5:3b | Which Ollama model to use |

Format names: `docx doc odt pdf pptx xlsx csv html json xml py ipynb log zip`

Files are saved in the `output` folder.

Examples:

```
python test_run.py "Create a project report for an AI based attendance system" --name demo

python test_run.py "Business proposal for a campus food delivery app" --type "Business Proposal" --formats docx,pdf --name food_proposal

python test_run.py "Startup pitch deck for a study planner app" --type "Pitch Deck" --sections 8 --formats pptx --name pitch

python test_run.py "Monthly budget for a college fest with a table of expense categories and amounts" --formats xlsx,csv --name fest_budget

python test_run.py "Hackathon project proposal" --formats docx,pdf,pptx,zip --name hackathon
```

If you want an Excel file with data sheets and a chart, mention a table in your prompt. The model often skips tables unless you ask for one.

Using it from your own Python code:

```python
from llm import generate_document
from renderers import render_all

doc = generate_document("Create a project report for an attendance system", "Project Report", 6)
paths = render_all(doc, outdir="output", base="demo", formats=("docx", "pdf", "pptx"))
```

To add a new format, create `renderers/myformat_r.py` with a `render(doc, path)` function and register it in `renderers/__init__.py`.

---

## Known drawbacks

I would rather be upfront about what this project cannot do well yet.

1. **The model is limited by the hardware it was built on.** The default 3B model was chosen because it runs on a normal laptop. It writes acceptable text but it can be generic, repeat itself, and sometimes invent numbers or facts. Treat every output as a first draft and read it before using it. Bigger models fix a lot of this, so use one if your computer can handle it.
2. **It can be slow.** On modest hardware a full document can take a minute or more. The first run is slower because Ollama has to load the model into memory.
3. **Tables are not guaranteed.** Small models skip them often. Without a table, the Excel file only has the overview sheet and no chart.
4. **Sections can fail.** If the model gives invalid output three times, that section gets placeholder text. The `.log` file shows which ones.
5. **The layout is basic.** There are no images, logos or custom templates. Charts only appear in Excel. Long bullet points can overflow a PowerPoint slide because the text does not shrink automatically.
6. **Some formats are simple.** The `.doc` file is RTF in disguise, and the `.odt` and `.html` outputs have light styling.
7. **Only English prompts have been tried.** Other languages depend on what the model supports.
8. **No enforced offline mode yet.** The program makes no internet calls, but it does not block them in code either.
9. **No graphical interface yet.** It runs from the command line.
10. **Developed and tested on Windows.** macOS and Linux should work but have had less testing.

---

## Troubleshooting

| Problem | What to do |
|---|---|
| `No module named 'ollama'` | The packages are not installed for the Python you are running. Activate the venv and run `pip install -r requirements.txt` |
| `can't open file ... test_run.py` | You are in the wrong folder. Go to the folder that contains `test_run.py` |
| PowerShell says running scripts is disabled | Run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`, or use Command Prompt |
| Connection refused | Ollama is not running. Start the Ollama app and try `ollama list` |
| `model not found` | Run `ollama pull <model name>` |
| Very slow or the computer freezes | The model is too big for your RAM. Run `python check_system.py` and pick a smaller one |
| "Content could not be generated" in a section | Run it again, or use a larger model |
| Excel file only has an Overview sheet | Ask for a table in your prompt |

---

## Tech stack

| Area | Tool | Used for |
|---|---|---|
| Language | Python 3.9+ | Everything |
| Local AI runtime | Ollama | Runs the language model on your machine |
| Language model | Qwen 2.5 (default), Llama 3.1 (optional) | Writes the outline and sections |
| Data validation | Pydantic | JSON schema and checking model output |
| Word | python-docx | .docx files |
| PDF | ReportLab | .pdf files |
| PowerPoint | python-pptx | .pptx files |
| Excel | openpyxl | .xlsx files and charts |
| OpenDocument | odfpy | .odt files |
| Standard library | csv, json, xml.etree, zipfile, html | CSV, JSON, XML, ZIP and HTML output |
| Charts | matplotlib | Listed for planned chart support |
| Interface | Streamlit | Listed for the planned web interface |

---

## Plans

1. A Streamlit web interface with format checkboxes and download buttons
2. Editing the outline before the full document is written
3. A guard in the code that blocks all non local network calls
4. Document templates such as resume and meeting minutes
5. Charts in Word, PDF and PowerPoint

---

## Testing

```
python test_render_only.py
```

This creates sample files in every format and checks that each one is valid. It does not need Ollama.

---
