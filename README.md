# Beyond the Yellow Tape: Investigating Global Homicide Rates

This project is an interactive Streamlit dashboard, with app.py as its main entry point. It uses Plotly visualisations to explore homicide patterns and compare whether countries with similar intentional homicide rates have different homicide profiles.

**Course:** DS608 Data Analytics for Economics, MDSE  
**Group members:** Paavas Bansal and Nehantha Sathesh   
**Live dashboard:** [Add deployed Streamlit URL]

## Motivation and objective

Intentional homicide is an important indicator of public safety, but overall rates do not fully describe who is affected or the circumstances of lethal violence.

Our research question is: **Can countries with similar intentional homicide rates exhibit significantly different homicide profiles?**

We aim to visualise global homicide patterns, compare victim characteristics and incident circumstances across countries, and examine changes over time. The analysis will support informed exploration rather than causal conclusions.

## Data sources

The project uses the **United Nations Office on Drugs and Crime (UNODC) Intentional Homicide dataset**, available through the UNODC Data Portal.

Variables considered, where available, include:

- Country, region, and year.
- Total victims and homicide rates per 100,000 population.
- Victim sex and age.
- Killing mechanisms, victim-perpetrator relationships, situational contexts, and citizenship.

Complete the following before submission:

| Detail | Project information |
| --- | --- |
| Exact dataset/download links | [Add links for each source file] |
| Download date and version | [Add details] |
| Countries and years included | [Add final coverage] |
| Original filenames and formats | [Add details] |
| Licence and redistribution terms | [Record applicable terms] |

Small datasets may be included when redistribution is permitted. Large or restricted datasets will be excluded using `.gitignore`. Public availability alone does not establish redistribution permission.

## Analytical approach

1. Inspect source definitions, units, and coverage.
2. Clean and restructure the data using Python, standardise country identifiers, and prepare comparable country-year records.
3. Identify missing observations and document their treatment, distinguishing missing data from zero counts.
4. Compare overall rates and available demographic and incident profiles using consistent periods where possible.
5. Develop Plotly visualisations and a Streamlit dashboard.

**Final decisions and justification:** [Explain selected periods, inclusion criteria, missing-data handling, derived measures, and reasons for the final analytical choices.]

## Streamlit dashboard
The dashboard will be implemented in app.py, using Streamlit for the interface and user controls, and Plotly for interactive charts.
- **Global overview:** Interactive choropleth world map of homicide rates.
- **Country comparison:** Side-by-side comparisons of two selected countries, covering overall rates, victim demographics, killing mechanisms, and other available characteristics.
- **Historical trends:** Line charts showing changes over time.
- **Data coverage:** Clear identification of gaps and comparison periods.

## Repository structure
```text
project/
|-- README.md
|-- AI_USAGE.md
|-- CONTRIBUTIONS.md
|-- .gitignore
|-- app.py
|-- requirements.txt
|-- data/
|   |-- raw/
|   |-- processed/
|-- src/
|   |-- wrangle.py
|-- outputs/
|   |-- figures/
|   |-- tables/
|   |-- presentation/
```
## Setup and execution

### 1. Obtain the project

Clone or download this repository and open a terminal in the repository root.

**Repository URL:** [Add shared GitHub URL]  
**Tested Python version:** [Add version]

### 2. Create the environment

```bash
python -m venv .venv
```

Activate it using the command for your system:

```bash
# Git Bash on Windows
source .venv/Scripts/activate

# macOS/Linux Bash
source .venv/bin/activate
```

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

### 3. Obtain the original data

1. Open the exact source links listed above.
2. Download [specify tables, filters, and export formats].
3. Create `data/raw/` if necessary and place the files there.
4. Use these filenames: [list exact expected filenames].

**Credentials:** [State whether credentials are needed. If required, document environment-variable names and setup without exposing values.]

### 4. Generate processed data

Run the wranglincg script to generate the processed data:

```bash
python src/wrangle.py
```

**Inputs and outputs:** [List raw input files, generated files in `data/processed/`, and any additional steps for reproducing figures, tables, or analysis.]

### 5. Run the dashboard

To run the dashboard the command is:

```bash
python -m streamlit run app.py
```

Open the local address shown in the terminal. Ensure that the deployed app can also obtain its required data; ignored files on a developer's laptop are not automatically available in deployment.

## Key findings and final outputs

- **Findings:** [Summarise results with countries, reference years, units, interpretation, and qualifications.]
- **Visualisations:** [Embed or link final figures and explain their messages.]
- **Figures:** `outputs/figures/`
- **Tables:** `outputs/tables/`
- **Presentation:** [Link final deck in `outputs/presentation/`]

The repository will include the presentation and relevant final figures and tables.

## Limitations and responsible interpretation

- Reporting standards and availability vary across countries and years, limiting comparability.
- Detailed victim and incident characteristics may have less complete coverage than overall rates.
- Missing values must not be interpreted as zero homicide.
- Comparisons should clearly identify reference periods and use consistent periods where possible.
- Descriptive patterns do not establish causal relationships.
- Sensitive crime statistics require care to avoid unsupported conclusions or misleading characterisations of countries and populations.

**Additional limitations:** [Add issues discovered during analysis and restrictions that prevent exact reproduction.]

## Ignored files and reproducibility

The `.gitignore` excludes local virtual environments, Python caches, notebook checkpoints, credentials, and temporary files. Passwords, API keys, access tokens, and `.env` files must not be committed.

**Excluded datasets and other relevant files:** [List the actual exclusions, explain why each is excluded, and provide instructions or code to obtain or regenerate them. State explicitly if no datasets are excluded.]

## AI usage and contributions

This is an **MDSE group project** completed by Paavas Bansal and Nehantha Sathesh.

- [AI_USAGE.md](AI_USAGE.md) will document whether and how GenAI was used, the tools used, and how outputs were reviewed, modified, or verified. Include documentation assistance where applicable.
- [CONTRIBUTIONS.md](CONTRIBUTIONS.md) will describe each member's contributions to data preparation, analysis, visualisation, dashboard development, documentation, presentation, and review.

