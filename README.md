# Beyond the Yellow Tape: Investigating Global Homicide Rates

**Can countries with similar intentional homicide rates exhibit different homicide profiles?**

*Beyond the Yellow Tape* is an interactive data analytics dashboard developed using Python, Pandas, Streamlit and Plotly. It explores global patterns in intentional homicide and examines how countries with similar overall homicide rates may differ in victim characteristics, mechanisms of killing and incident circumstances. Rather than focusing exclusively on the overall homicide rate, the project investigates the composition of recorded homicide victims to provide a more detailed understanding of lethal violence across countries.

**Course:** DS608 Data Analytics for Economics, Master of Science in Data Science in Economics (MDSE), Singapore Management University  
**Group members:** Paavas Bansal and Nehantha Sathesh   

---

## Accessing the Dashboard

The Beyond the Yellow Tape dashboard is publicly accessible through the link below:

[https://beyond-the-yellow-tape.streamlit.app/](https://beyond-the-yellow-tape.streamlit.app/)

**To reproduce the analysis and run the Streamlit dashboard locally please refer to section 6: Setup and Execution**

The dashboard allows users to explore global intentional homicide patterns between 2015 and 2024 without downloading the repository or installing Python.

Users can interact with two main sections:

**Global Overview:** Explore the geographic distribution of homicide rates, country rankings and historical trends.

**Compare Countries:** Identify countries with similar homicide rates and examine differences in recorded victim characteristics, mechanisms of killing and situational contexts.

For more informed country comparisons, users are encouraged to consult the Data Availability Table, which identifies the number of reported subcategories for each country and year.

The table is a preliminary screening tool and does not guarantee complete or directly comparable category-level reporting.

---

## 1. Motivation and Research Objective

Intentional homicide is an important indicator of public safety and lethal violence. It is commonly measured through the number of homicides per 100,000 people, allowing comparisons across countries with different population sizes.

However, overall homicide rates do not fully describe the characteristics or circumstances of lethal violence.

Two countries may have similar homicide rates but differ considerably in:

- The demographic composition of homicide victims.
- The mechanisms through which homicides occur.
- The relationship between victims and perpetrators.
- The circumstances in which homicides take place.
- Changes in homicide rates over time.

### Research Question

**Can countries with similar intentional homicide rates exhibit substantially different homicide profiles?**

The objective of this project is to develop an interactive dashboard that allows users to explore global homicide patterns, identify countries with similar overall rates and investigate differences in their recorded homicide profiles.

The analysis is descriptive and exploratory. It aims to identify patterns and differences that warrant further investigation rather than establish causal relationships.

---

## 2. Data Sources

### UNODC Intentional Homicide Dataset

The project uses publicly available intentional homicide statistics from the **United Nations Office on Drugs and Crime (UNODC)**.

**Source:** [UNODC Intentional Homicide Data Portal](https://data.unodc.org/datareport/hom-victim)  
**Download date:** 25 October 2026  
**Time period:** 2015-2024  
**Original file:** `total_count_intentional_homicide.xlsx`  
**Primary population of interest:** Victims of intentional homicide, with age aggregated to the total category

The original dataset includes country-year observations for overall homicide counts and rates, together with more detailed classifications where available.

### Variables Used

| Dimension | Description |
|---|---|
| Overall homicide | Intentional homicide counts and rates per 100,000 population |
| Victim sex | Female and male homicide victims |
| Mechanism of killing | Firearms, other weapons, unarmed mechanisms and unspecified mechanisms |
| Victim–perpetrator relationship | Intimate partner or family member, other known perpetrator, unknown perpetrator and related classifications |
| Situational context | Organized crime or gangs, interpersonal homicide, other criminal activities and other classifications |
| Citizenship | National and foreign-citizen homicide victims |
| Time | Annual observations from 2015 to 2024 |

Not all countries report observations for every dimension or category. Coverage varies considerably across countries and years.

The underlying dataset also contains additional information not incorporated into every dashboard visualisation.

### Data Access and Redistribution

The original UNODC workbook is obtained from the public data portal and stored locally under `data/raw/`.
The repository does not require redistribution of the original workbook. Users wishing to reproduce the analysis should obtain the dataset directly from UNODC and consult the source's applicable usage and attribution terms.

Six processed CSV files derived from the source dataset are included in the repository to support the public Streamlit dashboard. These contain the cleaned and restructured observations required for the application's visualisations.
The processing code is provided in src/wrangle.py to document the transformations applied to the original data.

---

## 3. Analytical Approach

The project follows a data-processing and visualisation workflow using Python and Pandas.

### 3.1 Data Cleaning and Restructuring

The original UNODC data was filtered to retain the relevant intentional homicide observations between 2015 and 2024.

The dataset was then restructured to support country-year analysis, including:

1. Validating required source columns and standardising text fields and country identifiers.
2. Converting numeric observations to appropriate data types.
3. Separating and aligning homicide counts and rates.
4. Identifying duplicate observations.
5. Retaining missing observations rather than treating them as zero.
6. Organising the different homicide dimensions into processed datasets.

The six processed CSV files are stored in `data/processed/` and committed to GitHub for use by the public Streamlit dashboard.

### 3.2 Treatment of Missing Data

Missing observations are an important consideration because reporting coverage differs across countries and years.

Where supported by the preprocessing pipeline, short internal gaps of up to two consecutive years are filled using linear interpolation.

Interpolated observations are flagged so that they can be distinguished from directly reported values. Longer gaps are not automatically filled.

This approach improves continuity for exploratory analysis but does not eliminate the uncertainty associated with missing data.

### 3.3 Derived Measures

Where suitable homicide counts and rates are available, population denominators can be inferred using:

\[
\text{Population} = \frac{\text{Homicide Count}}{\text{Homicide Rate per 100,000}} \times 100{,}000
\]

These denominators may be used to derive additional rates where appropriate.

Derived and imputed observations are distinguished from directly reported observations where the relevant quality flags are available.

### 3.4 Constructing Homicide Profiles

For detailed comparisons, the project uses category-level counts to construct shares describing the composition of recorded homicide victims.

These profiles include victim sex, mechanisms of killing, victim–perpetrator relationships, situational contexts and citizenship.

Care is taken to avoid double counting where categories contain hierarchical or nested classifications. The interpretation of shares depends on the availability and completeness of the relevant reported categories.

**Importantly, victim shares should not be interpreted as population-level homicide risks.**

For example, if women account for 30% of recorded homicide victims in a country, this indicates the female proportion of recorded victims in that breakdown. It does not mean that women have a 30% probability of being murdered.

### 3.5 Tools and Technologies

| Tool | Purpose |
|---|---|
| Python | Data processing and application development |
| Pandas | Data cleaning, restructuring, aggregation and availability analysis |
| NumPy | Numerical operations |
| Plotly Express | Interactive maps and charts |
| Plotly Graph Objects | Customised comparative visualisations |
| Streamlit | Dashboard interface, user controls and visualisation integration |
| Jupyter Notebook | Exploratory analysis and generation of the availability table |
| Git and GitHub | Version control, collaboration and project documentation |

---

## 4. Streamlit Dashboard

The dashboard is divided into two primary sections: **Global Overview** and **Compare Countries**.

### 4.1 Global Overview

The Global Overview provides an interactive exploration of homicide rates across countries and years.

**Global Homicide Map**

- Interactive world choropleth displaying intentional homicide rates.
- Dropdown to select a year between 2015 and 2024, subject to data availability.
- Hover information displaying country-level statistics and data-quality information.
- Colour intensity representing the overall homicide rate.

**Country Rankings**

- Identification of countries with the highest available homicide rates for the selected year.
- Interactive bar chart and supporting data table.

**Global Homicide Trends**

- Historical trends in the median country homicide rate.
- Changes in the number of countries with available observations.
- Trends in the sum of available recorded homicide counts.

The median country rate should not be interpreted as a population-weighted global homicide rate.

**What Changed? Country Rate Explorer**

- Comparison of homicide rates between two selected years.
- Identification of countries experiencing the largest increases or decreases.
- Examination of absolute and percentage changes.
- Distinction between directly reported and imputed observations where available.

### 4.2 Compare Countries

The Compare Countries section allows users to investigate differences between two selected countries.

**Similar-Rate Country Finder**

Users can select a country and identify others with similar overall intentional homicide rates for the selected year.

Countries are ranked according to the absolute difference between their homicide rates.

The finder identifies similarity in overall rates only. It does not guarantee that the countries have comparable subcategory data.

**Country Homicide Profile Comparison**

Users can select two countries and compare available information on:

- Female victim shares.
- Sex composition among foreign or non-resident homicide victims, where available.
- Mechanisms of killing.
- Victim–perpetrator relationships.
- Situational contexts.
- Citizenship.
- Historical homicide-rate trends.

**Multi-Dimension Profile Comparison**

The dashboard also includes a combined comparison chart that allows users to examine multiple homicide dimensions together.

Users can select which dimensions to display while retaining their selected country pair.

The visualisation highlights differences in the composition of recorded homicide victims across the selected dimensions.

Shares from different dimensions should not be added together, as they describe different characteristics of overlapping victim populations.

---

## 5. Repository Structure

The project is organised as follows:

```text
608_Group_Project/
│
├── app.py
├── README.md
├── requirements.txt
├── .gitignore
├── AI_USAGE.md
├── CONTRIBUTIONS.md
│
├── src/
│   ├── wrangle.py
│   └── availability.ipynb
│
├── data/
│   ├── raw/                     # Local only (not tracked)
│   │   └── total_count_intentional_homicide.xlsx
│   │
│   └── processed/
│       ├── rates.csv
│       ├── sex.csv
│       ├── mechanism.csv
│       ├── relationship.csv
│       ├── context.csv
│       └── citizenship.csv
│
└── outputs/
    ├── figures/
    ├── tables/
    │   └── homicide_availability.csv
    └── presentation/
        # DS608_final_presentation.pdf

```

**Directory descriptions:**

- `app.py`: Main Streamlit application containing dashboard controls, layout and visualisations.
- `src/wrangle.py`: Preprocessing and transformation of the original homicide dataset.
- `src/availability.ipynb`: Jupyter notebook used to analyse subcategory reporting availability.
- `data/raw/`: Original downloaded data.
- `data/processed/`: Processed datasets used by the dashboard.
- `outputs/figures/`: Directory for exported figures, where applicable.
- `outputs/tables/`: Supporting analytical tables.
- `outputs/presentation/`: Final project presentation in PDF format.
- `AI_USAGE.md`: Documentation of generative AI assistance.
- `CONTRIBUTIONS.md`: Documentation of group-member contributions.
- 
### Data Storage and Repository Tracking

The original UNODC Excel dataset is stored locally in `data/raw/` and is not included in the GitHub repository.
The six processed CSV files required by the Streamlit dashboard are included in `data/processed/` and committed to GitHub to support deployment through Streamlit Community Cloud.
Although both `data/raw/` and `data/processed/` are listed in `.gitignore`, the six required processed CSVs have been explicitly added to Git tracking. Other untracked files in these directories remain ignored.
The preprocessing script also generates `coverage.csv`, which contains diagnostic information about reporting coverage. This file is not required by the dashboard and is not included in the repository.

---

## 6. Setup and Execution

The following instructions describe how to reproduce the analysis and run the Streamlit dashboard locally. This also includes how to produce processed dataset locally.

### Step 1 — Clone the Repository

Clone the repository:

```bash
git clone https://github.com/pbansal2026-sys/608_Group_Project.git
```

Navigate to the project directory:

```bash
cd 608_Group_Project
```

### Step 2 — Create a Python Virtual Environment

Create a virtual environment:

```bash
python -m venv .venv
```

Activate the environment.

**Windows — Git Bash:**

```bash
source .venv/Scripts/activate
```

**Windows — PowerShell:**

```powershell
.\.venv\Scripts\Activate.ps1
```

**macOS/Linux:**

```bash
source .venv/bin/activate
```

Install the required dependencies:

```bash
python -m pip install -r requirements.txt
```
**At this point the dashboard can be run locally because the six required processed CSV files are included in the repository. To launch it directly, skip to Step 5. To regenerate the processed datasets from the original UNODC data, complete Steps 3 and 4 first.**

### Step 3 — Obtain the Original UNODC Data

Visit the [UNODC Intentional Homicide Data Portal](https://data.unodc.org/datareport/hom-victim).

Obtain the intentional homicide dataset covering the relevant observations and period.

Save the workbook under:

```text
data/raw/total_count_intentional_homicide.xlsx
```

Ensure that the filename and directory structure match those expected by the preprocessing code.

The project uses the dataset downloaded on 25 October 2026. Subsequent UNODC revisions may produce differences in the reproduced results.

### Step 4 — Generate the Processed Data

From the repository root, run:

```bash
python src/wrangle.py
```

The preprocessing script generates the datasets required by the dashboard, including:

```text
data/processed/rates.csv
data/processed/sex.csv
data/processed/mechanism.csv
data/processed/relationship.csv
data/processed/context.csv
data/processed/citizenship.csv
```

These files must be present for the relevant dashboard visualisations to function.

### Step 5 — Run the Streamlit Dashboard locally

To run the dashboard locally, from the repository root, execute:

```bash
python -m streamlit run app.py
```

Open the local address displayed in the terminal, typically:

```text
http://localhost:8501
```
---

## 7. Data Availability Table

### 7.1 Motivation

A major challenge encountered during dashboard development was the uneven availability of disaggregated intentional homicide data.

Although two countries may have similar overall homicide rates, one or both may lack observations for specific homicide dimensions.

For example, a country may report its overall homicide count and rate but provide little information about the mechanism of killing or the victim's relationship with the perpetrator.

This limits the usefulness of some country comparisons, particularly when users wish to investigate detailed homicide profiles.

### 7.2 Our Approach

To help address this issue, we created a country-year data availability table using Python and Pandas.

The analysis examines subcategory reporting for countries between 2015 and 2024.

For each country-year observation, the table includes:

- The available overall intentional homicide rate.
- Counts of distinct subcategories with non-missing observations within selected homicide dimensions.

The table helps users identify countries and years with relatively stronger subcategory reporting.

It can therefore be used as a **preliminary guide for selecting potentially informative country comparisons** in the dashboard.

### 7.3 Accessing the Table

**[View the Homicide Data Availability Table](outputs/tables/homicide_availability.csv)**

To regenerate the availability table, obtain the original UNODC workbook and execute all cells available in:

**[Data Availability Analysis Notebook](src/availability.ipynb)**

Users can consult the table before selecting countries in the dashboard.

For instance, if two countries have similar overall homicide rates and both report several mechanism-of-killing categories, they may be promising candidates for a more detailed comparison.

However, the actual category-level information should still be checked in the dashboard.

### 7.4 Important Qualification

The availability table is intended as a **screening and exploratory tool**, not a definitive measure of cross-country comparability.

It records the number of reported subcategories, rather than verifying whether the same specific subcategories are present in both countries.

For example, two countries may each report three mechanism categories while reporting different mechanisms.

Furthermore, a greater number of reported categories does not necessarily imply complete reporting or higher data quality.

The limitations of this approach are discussed below.

---

## 8. Limitations

### 8.1 Uneven Data Availability

One of the main limitations of the analysis is that homicide reporting differs across countries and years.

Overall homicide counts and rates are generally more widely available than detailed victim and incident characteristics.

As a result, not every country pair can be meaningfully compared across every dimension.

Differences in national data collection and classification practices may further limit comparability.

### 8.2 Limitations of the Availability Table

Although the data availability table assists users in identifying potentially useful comparisons, it has several limitations:

- It counts the number of available categories but does not verify whether two countries report the same categories.
- It does not automatically establish whether the reported categories form a complete and mutually exclusive breakdown of all homicides.
- Countries with similar numbers of reported categories may still have substantially different reporting coverage.
- The existence of an observation does not guarantee equivalent reporting quality or definitions across countries.

Therefore, the table should be used as a preliminary guide rather than a guarantee that a country pair will produce complete, directly comparable visualisations.

### 8.3 Missing Data and Imputation

Missing observations are not equivalent to zero homicides. Some countries may have no reported observations for particular dimensions, while others may include unknown or unspecified classifications.

Short internal gaps are interpolated where supported by the preprocessing approach. However, interpolation assumes a relatively smooth path between observed values and may conceal abrupt changes.

### 8.4 Interpretation of Victim Shares

The detailed profile charts primarily describe the composition of recorded homicide victims. These shares should not be interpreted as the probability of an individual experiencing homicide.

### 8.5 Limitations of Similar-Rate Matching

The similar-rate country finder identifies countries based on the absolute difference between their homicide rates for a selected year. The matching procedure is therefore descriptive rather than a statistical matching or causal identification method.

### 8.6 No Causal Interpretation

The dashboard identifies patterns, associations and differences in homicide statistics. It does not establish the causal mechanisms responsible for those patterns.

---

## 9. Final Outputs

The project consists of the following deliverables:

| Deliverable | Description | Location |
|---|---|---|
| Streamlit dashboard | Interactive exploration of global homicide patterns and country profiles | `app.py` |
| Data preprocessing | Cleaning and restructuring of the UNODC dataset | `src/wrangle.py` |
| Processed datasets | Six cleaned and restructured CSV files required for the dashboard, included in the repository for public deployment | `data/processed/` |
| Data availability analysis | Country-year assessment of reported subcategories | `src/availability.ipynb` |
| Availability table | Supporting CSV for identifying potentially informative comparisons | [`outputs/tables/homicide_availability.csv`](outputs/tables/homicide_availability.csv) |
| Presentation | Summary of project motivation, methodology, findings and limitations (PDF) | [`outputs/presentation/DS608_final_presentation.pdf`](outputs/presentation/DS608_final_presentation.pdf) |
| AI usage documentation | Record of generative AI assistance and review | [AI_USAGE.md](AI_USAGE.md) |
| Group contributions | Documentation of individual contributions | [CONTRIBUTIONS.md](CONTRIBUTIONS.md) |

---

## 10. Reproducibility and Repository Management

The project uses Git and GitHub for version control, collaboration and source-code documentation.
To support public deployment through Streamlit Community Cloud, the six processed CSV files required by the dashboard are committed to the repository under `data/processed/`.
These files enable users to run the application directly without downloading or preprocessing the original UNODC dataset.
The original UNODC Excel workbook is not included in the repository. Users wishing to reproduce the full data-processing pipeline can obtain the source data from the UNODC Data Portal and execute `src/wrangle.py` using the instructions provided above.
The `.gitignore` configuration excludes the original raw data, virtual environments, Python caches, temporary files and untracked generated data. Although `data/processed/` is listed in `.gitignore`, the six CSV files required by the dashboard have been explicitly committed and remain tracked by Git.

Other locally generated datasets, including `coverage.csv`, are not required for the public dashboard and remain excluded from the repository.
The data availability analysis is documented separately through `src/availability.ipynb`, with its resulting CSV provided under `outputs/tables/`.
This arrangement balances reproducibility, repository size and ease of deployment by providing the datasets necessary to operate the dashboard while retaining the original preprocessing code for users who wish to reproduce the analysis.

---

## 11. AI Usage and Group Contributions

This project was completed as part of the MDSE programme at Singapore Management University.

**Group members:**
- Paavas Bansal
- Nehantha Sathesh

Generative AI assistance and individual contributions are documented separately to provide transparency about the development process.

- **[AI Usage Documentation](AI_USAGE.md):** Describes the use of generative AI tools during project development and how generated outputs were reviewed or modified.
- **[Group Contributions](CONTRIBUTIONS.md):** Describes the contributions of each group member to data preparation, analysis, visualisation, development, documentation and presentation.
