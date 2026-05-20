# Dataset Setup

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
docker compose build --no-cache
```
For manual local execution outside Docker, install:
```bash
pip install kaggle
```

Inside the container, verify:

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
From the project root directory, start the Docker app container:

```bash
docker compose up -d app
docker compose exec app bash
```
Inside the container, run:
```bash
python3 scripts/download_data.py
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
Dataset probably already exists in `data/raw`

### 5.3 `kaggle --version` fails
Ensure kaggle is installed
```bash
pip install kaggle
```
- Ensure `kaggle.json` is correctly placed in .kaggle directory

--- 
### Note:
The script is safe to run multiple times
