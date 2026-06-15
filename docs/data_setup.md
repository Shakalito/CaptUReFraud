# Dataset Setup

This project requires downloading a dataset from Kaggle.

The dataset can be downloaded manually or using the provided script.
The script stores the dataset in the project directory under `data/raw/`.

---

## 1. Create Kaggle API Token

1. Go to: https://www.kaggle.com/settings
2. Scroll to **API**
3. Click **Create New API Token**
4. A file named `kaggle.json` will be downloaded

---

## 2. Configure Kaggle API

### Windows

1. Create folder:
`C:\Users\<your-username>\.kaggle\`
2. Move `kaggle.json` into this folder:
`C:\Users\<your-username>\.kaggle\kaggle.json`

### Linux / macOS

Run:
```bash
mkdir -p ~/.kaggle
mv kaggle.json ~/.kaggle/
chmod 600 ~/.kaggle/kaggle.json
```
---
## 3. Install dependencies

The recommended workflow is Docker-based. Build the image from the project root:

```bash
docker compose build
```

The startup scripts can also run the dataset setup automatically:

```bash
./start.sh
```

On Windows:

```powershell
.\start.bat
```

For manual local execution outside Docker, install:
```bash
pip install kaggle
```

Verify that the Kaggle CLI is available:

```bash
kaggle --version
```

If the command works, you should see something like:
```bash
Kaggle CLI x.x.x
```
If not, go to the troubleshooting section.

---
## 4. Download dataset

From the project root directory, run:

```bash
python scripts/download_data.py
```

On Windows:

```powershell
python scripts\download_data.py
```

The dataset will be saved to:

```text
data/raw/
```

The script is safe to run multiple times. If a CSV file already exists in `data/raw/`, the download step is skipped.

---
## 5. Manual download option

If Kaggle API is not configured, download the dataset manually from:

```text
https://www.kaggle.com/datasets/rupakroy/online-payments-fraud-detection-dataset
```

Then place the CSV file in:

```text
data/raw/
```

Expected file:

```text
data/raw/PS_20174392719_1491204439457_log.csv
```

---
## 6. Troubleshooting

### 6.1 If kaggle.json was not downloaded automatically
You can create it manually.

Create a file `kaggle.json`
With content:

```json
{
  "username": "your_kaggle_username",
  "key": "your_api_key"
}
```

You can find:
```bash
username → your Kaggle profile name
key → from Kaggle API section
```

### 6.2 Script does nothing
Dataset probably already exists in `data/raw/`.

### 6.3 `kaggle --version` fails
Ensure kaggle is installed:

```bash
pip install kaggle
```

Also ensure `kaggle.json` is correctly placed in the `.kaggle` directory.

### 6.4 Dataset is saved outside the project directory
Run the current version of `scripts/download_data.py` from the project root.
The script resolves the project directory automatically and writes to `data/raw/`.

--- 
### Note

Raw data is not tracked by Git.
