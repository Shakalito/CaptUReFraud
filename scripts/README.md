# Dataset Setup (Kaggle)

This project requires downloading a dataset from Kaggle.

The dataset can be downloaded manually or using the provided script,
which ensures a reproducible setup.

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
`C:\Users<your-username>\.kaggle\`
2. Move `kaggle.json` into this folder:
`C:\Users<your-username>\.kaggle\kaggle.json`

### Linux / macOS

Run:
```bash
mkdir -p ~/.kaggle
mv kaggle.json ~/.kaggle/
chmod 600 ~/.kaggle/kaggle.json
```
---
## 3. Install dependencies 
(If not already installed via requirements.txt)
```bash
pip install kaggle
```
After installing Kaggle, verify that it works:

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
From project root directory:
```bash
python scripts/download_data.py
```
The dataset will be saved to: `data/raw`

---
## 5. Troubleshooting

### 5.1 If kaggle.json was not downloaded automatically
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
### 5.2 Script does nothing
Dataset propably already exists in data/raw

### 5.3 `kaggle --version` fails
Ensure kaggle is installed
```bash
pip install kaggle
```
- Ensure `kaggle.json` is correctly placed in .kaggle directory

### 5.4 Different problems
All the answears are under this [link](https://letmegooglethat.com/?q=why+doesn%27t+it+work%3F)

--- 
### Note:
The script is safe to run multiple times