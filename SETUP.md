# Setup guide: run the workshops on your own laptop

This course uses two databases, **MongoDB** (document database) and **Neo4j** (graph database).
Instead of installing them by hand, we run both inside **Docker containers**: a container is a small, isolated, pre-configured mini-computer.
One command starts everything, and removing it later leaves no trace on your laptop.

> ⏱️ **Time:** 20-30 minutes the first time (most of it is downloading). **Disk:** ~4 GB. **RAM:** 8 GB laptop recommended (the databases use ~1.5 GB).
> **Internet:** only needed *once*, to download Docker, the database images and the Python packages. Afterwards everything works offline.

```
 your laptop
 ├── JupyterLab (Python)  ── runs the workbooks
 │        │  talks to ▼
 └── Docker
      ├── 🍃 MongoDB  container  → localhost:27017
      └── 🔵 Neo4j    container  → localhost:7687 (Bolt)  and  http://localhost:7474 (web UI)
```

## Checklist

- [ ] **Step 1** Get the course materials
- [ ] **Step 2** Install Docker
- [ ] **Step 3** Start MongoDB and Neo4j
- [ ] **Step 4** Create a Python environment and install the packages
- [ ] **Step 5** Check that everything works
- [ ] **Step 6** Open the workbooks

---

## Step 1 · Get the course materials

With **git** (recommended):

```bash
git clone https://github.com/St-Jude-MS-ABDS/workshop-NoSQL.git
cd workshop-NoSQL
```

Without git: on the GitHub page click **Code ▸ Download ZIP**, unzip it, and open a terminal in the unzipped folder.

> **What is a "terminal"?** macOS: *Terminal* app · Windows: *PowerShell* (Start menu) · Linux: your terminal app.
> All commands below are typed there. `cd folder` means "go into that folder".

What is in the folder (the ones you will use):

| folder / file | what it is |
|---|---|
| `docker/` | `docker-compose.yml`: the recipe that starts MongoDB and Neo4j |
| `data/` | all data files used in the workshops (nothing else to download!) |
| `2-mongodb-workshop/` | Lecture 25 workbook (MongoDB) |
| `3-graphdb-concept/` | Lecture 26 workbook (graph basics) |
| `4-neo4j-workshop/` | Lecture 27 workbook (genome graph in Neo4j) |
| `scripts/check_setup.py` | a script that tests your installation |
| `requirements.txt` | the Python packages |

---

## Step 2 · Install Docker

<details open><summary><b>🍎 macOS</b></summary>

1. Download **Docker Desktop** from <https://www.docker.com/products/docker-desktop/> (choose *Apple Silicon* for M1/M2/M3/M4 Macs, *Intel chip* otherwise: Apple menu ▸ *About This Mac* tells you).
2. Open the `.dmg`, drag Docker to *Applications*, **start it** and accept the prompts. Wait until the whale icon in the menu bar says *"Docker Desktop is running"*.
</details>

<details><summary><b>🪟 Windows 10 / 11</b></summary>

1. Download and install **Docker Desktop** from <https://www.docker.com/products/docker-desktop/>. Keep the option **"Use WSL 2 instead of Hyper-V"** ticked. (If asked, allow it to install WSL 2 and **restart**.)
2. Start Docker Desktop and wait until it says it is running.
3. If Docker complains about *virtualization*, it must be switched on in the BIOS/UEFI: search for "enable virtualization" together with your laptop model.
4. Run all commands in this guide in **PowerShell**.
</details>

<details><summary><b>🐧 Linux (Ubuntu / Debian example)</b></summary>

Follow the official guide to install **Docker Engine + the Compose plugin**: <https://docs.docker.com/engine/install/>. Then allow your user to use Docker without `sudo`, and log out and in again:

```bash
sudo usermod -aG docker $USER
```
</details>

> 🏥 **Managed laptop (hospital / university)?** Docker Desktop may require admin rights. Ask your IT help desk for it, or use a free alternative such as *Rancher Desktop*, *Colima* (macOS) or *Podman*. Any tool that provides the `docker compose` command works.
> **Licence note:** Docker Desktop is free for education, personal use and small businesses; larger companies need a paid plan.

**Test the installation** (each command should print a version / a welcome message, not an error):

```bash
docker --version
docker compose version
docker run --rm hello-world
```

---

## Step 3 · Start MongoDB and Neo4j

```bash
cd docker
docker compose up -d
```

* `up` creates and starts the containers; `-d` ("detached") gives your terminal back.
* **The first time**, Docker downloads the database images (~1.5 GB). This can take several minutes; later starts take seconds.

Now check the status, repeating the command until both lines say **`healthy`** (Neo4j needs about 30 seconds):

```bash
docker compose ps
```

```
NAME                     IMAGE                  STATUS                   PORTS
nosql-workshop-mongodb   mongo:7.0              Up 40 seconds (healthy)  127.0.0.1:27017->27017/tcp
nosql-workshop-neo4j     neo4j:5.26-community   Up 40 seconds (healthy)  127.0.0.1:7474->7474/tcp, 127.0.0.1:7687->7687/tcp
```

### What is running, and how to reach it

| | address | user | password | used in |
|---|---|---|---|---|
| **MongoDB**: administrator | `mongodb://localhost:27017` | `admin` | `workshop_admin` | the admin step of Lecture 25 |
| **MongoDB**: student | `mongodb://localhost:27017` | `student` | `student_password` | Lecture 25 (restricted account, on purpose) |
| **Neo4j** Bolt (Python) | `bolt://localhost:7687` | `neo4j` | `workshop_neo4j` | Lectures 26-27 |
| **Neo4j Browser** (web UI) | <http://localhost:7474> | `neo4j` | `workshop_neo4j` | optional: draw graphs and type Cypher by hand |

> These passwords are public on purpose: the databases only listen on `127.0.0.1` (your own laptop) and contain teaching data only. **Never reuse them anywhere else.**

### Daily commands (run inside the `docker/` folder)

| I want to ... | command |
|---|---|
| see what is running | `docker compose ps` |
| pause the databases (data is **kept**) | `docker compose stop` |
| start them again | `docker compose start` (or `up -d`) |
| read the log of a database | `docker compose logs -f neo4j` (leave with `Ctrl+C`) |
| remove the containers (data is **kept** in volumes) | `docker compose down` |
| **delete everything** (all data), for a clean restart | `docker compose down -v` |
| free the disk space of the images afterwards | `docker image rm mongo:7.0 neo4j:5.26-community` |

---

## Step 4 · Python environment

You need **Python 3.10 or newer** (`python3 --version`; get it from <https://www.python.org/downloads/> if needed).
A *virtual environment* keeps this course's packages separate from everything else on your computer. From the **repository root** (the folder that contains `requirements.txt`):

**macOS / Linux**

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

**Windows (PowerShell)**

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1          # if PowerShell refuses: Set-ExecutionPolicy -Scope Process Bypass   (then repeat)
pip install -r requirements.txt
```

Your prompt now starts with `(.venv)`. **Every time you open a new terminal** for the workshops, activate the environment again (the `source ...` / `Activate.ps1` line).

<details><summary>Using conda / mamba instead?</summary>

```bash
conda create -n nosql-workshop python=3.12 -y
conda activate nosql-workshop
pip install -r requirements.txt
```
</details>

---

## Step 5 · Check that everything works

From the repository root, with the environment activated:

```bash
python scripts/check_setup.py
```

You should see only ✅ lines and *"🎉 Everything is ready"*. Every ❌ line comes with a "→" hint on how to fix it.

---

## Step 6 · Open the workbooks

```bash
jupyter lab
```

A browser tab opens. In the file browser on the left, open the workbook of the day (double-click `workbook.ipynb`):

| Lecture | folder | topic |
|---|---|---|
| 25 | `2-mongodb-workshop/` | MongoDB: RBAC, CRUD, indexes, aggregation (VCF data) |
| 26 | `3-graphdb-concept/` | Graph basics with Neo4j and Cypher |
| 27 | `4-neo4j-workshop/` | Build and query a genome graph |

Run a cell with **Shift + Enter**. The notebooks explain every step; work through them from top to bottom.

---

## Optional tools

* **Neo4j Browser**: <http://localhost:7474>. Try `MATCH (n) RETURN n LIMIT 25` after Lecture 27's import. Great for *seeing* the graph.
* **MongoDB Compass** (free GUI): <https://www.mongodb.com/products/tools/compass>, connect with `mongodb://student:student_password@localhost:27017/?authSource=admin`.
* **A shell inside the databases**:
  `docker exec -it nosql-workshop-mongodb mongosh -u student -p student_password --authenticationDatabase admin`
  and `docker exec -it nosql-workshop-neo4j cypher-shell -u neo4j -p workshop_neo4j`.
* **GitHub Codespaces**: the repository contains a `.devcontainer/` configuration; open a Codespace, then follow Steps 3 and 5 in its terminal (Docker is available in the default image).

---

## Troubleshooting

| Problem | What it means / how to fix it |
|---|---|
| `Cannot connect to the Docker daemon` / `docker: command not found` | Docker Desktop is not running (or not installed). Start it and wait for "running". |
| `Bind for 127.0.0.1:27017 failed: port is already allocated` | **Another MongoDB (or container) already uses that port.** Use another port: create a file `docker/.env` containing `MONGO_PORT=27018` and run `docker compose up -d` again. Then tell the notebook: start Jupyter with the same variable (`MONGO_PORT=27018 jupyter lab` on macOS/Linux; PowerShell: `$env:MONGO_PORT=27018; jupyter lab`). Same idea for Neo4j: `NEO4J_HTTP_PORT` and `NEO4J_BOLT_PORT`. |
| `docker compose ps` shows `starting` for a long time, or `unhealthy` | Wait 1-2 minutes. Then read the log: `docker compose logs neo4j`. Low memory is a common cause: close other programs, or give Docker more RAM (Docker Desktop ▸ Settings ▸ Resources). |
| `Authentication failed` in a notebook | wrong user/password: use the table in Step 3. |
| The restricted `student` user does not exist | MongoDB creates it **only the first time** the data volume is empty. Fix: `docker compose down -v`, then `docker compose up -d`. |
| `ModuleNotFoundError: No module named 'neo4j'` (or `pymongo`, `vcfpy` ...) | the notebook runs in the wrong Python. Activate `.venv` *before* starting `jupyter lab`, or run `python -m ipykernel install --user --name nosql-workshop` inside the environment and choose that kernel in Jupyter (*Kernel ▸ Change Kernel*). |
| `pip install` fails with a certificate / proxy error | you are probably behind a company proxy: ask IT for the proxy settings (`pip install --proxy http://host:port ...`) |
| `no matching manifest for linux/arm64` / platform warnings | harmless on Apple Silicon; both images have native ARM builds. |
| On **Windows**, the init script seems ignored | Make sure the repository was cloned with the original line endings; `git config --global core.autocrlf false`, then re-clone. (The MongoDB init file is robust to CRLF, but other editors may change it.) |
| `permission denied` on `/var/run/docker.sock` (Linux) | add your user to the `docker` group (Step 2, Linux) and log in again |
| I broke the databases / want a fresh start | `cd docker && docker compose down -v && docker compose up -d` |

Still stuck? Copy the **full error message** and the output of `docker compose ps` and ask your instructor or the course channel.
