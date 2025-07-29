- [Course Mock Session Preparation](#course-mock-session-preparation)
  - [Time and Place](#time-and-place)
  - [Mock Session Design Focus](#mock-session-design-focus)
  - [Session Format](#session-format)
  - [Learning Objectives](#learning-objectives)
  - [Course Design](#course-design)
- [Lecturer's Notes](#lecturers-notes)
  - [Diagrams](#diagrams)
    - [Poll website architecture](#poll-website-architecture)
    - [Poll workflow](#poll-workflow)
    - [SQL database scheme: poll as an example](#sql-database-scheme-poll-as-an-example)
    - [NoSQL database scheme: Document: poll as an example](#nosql-database-scheme-document-poll-as-an-example)
    - [NoSQL database scheme: Key-value: poll as an example](#nosql-database-scheme-key-value-poll-as-an-example)
    - [Evolution of Databases](#evolution-of-databases)
    - [Early Database Models: Hierarchical: poll as an example](#early-database-models-hierarchical-poll-as-an-example)
    - [Early Database Models: Network: poll as an example](#early-database-models-network-poll-as-an-example)
    - [Decision Tree for NoSQL Database Selection](#decision-tree-for-nosql-database-selection)
  - [Before going to the classroom](#before-going-to-the-classroom)
  - [In the classroom: preparation](#in-the-classroom-preparation)

# Course Mock Session Preparation

## Time and Place
The course mock up will be conducted on Tuesday, July 29, 9AM - 10AM in the ABDS classroom (ARC MP163). 

## Mock Session Design Focus
The mock session reviewers will pay attention to the following areas:
- Content & Objectives Alignment
  - Lecture objectives clear and stated?
  - Content aligned with objectives?
- Structure & Flow
  - Logical progression and appropriate pacing?
- Engagement & Delivery
  - Engaging and clear?
  - Are there opportunities for interaction?
  - Do you appear prepared and confident?
- Visuals & Materials
  - Are slides clear, readable, and aligned with the spoken content?
  - Do visuals support learning without overwhelming?
- Active Learning Integration
  - Are active learning strategies (polls, think-pair-share, discussion) effectively integrated?
  

## Session Format

Session time allocation provided by the course support team:
| Time | Activity |
| ---- | -------- |
| 5 min | Setup and technology check |
| 40 min | Your mock lecture delivery |
| 10 min | Feedback discussion |
| 5 min | Wrap-up and next steps |

## Learning Objectives

At the end of this session, participants will be able to:

- **Describe** the historical development and evolution of NoSQL databases in the context of modern data challenges. 
- **Identify** and **explain** real-world scenarios where NoSQL systems are preferred over traditional relational databases. 
- **Compare** different NoSQL data models (e.g., document, key-value, column-family, graph) and recognize popular systems that use each model (e.g., MongoDB, Cassandra, Redis). 


## Course Design

The course will be largely based on the [1-nosql-concept](1-nosql-concept/README.md) module, which covers the history of databases, the evolution of NoSQL systems, and their applications in bioinformatics and data science.

Here is a breakdown of the course design:

1. **Introduction of lecturers and course objectives** (5 minutes)
   - Briefly introduce the lecturers
   - Quick poll on codespace to gauge participants' familiarity with database concepts. [^poll]
   - Go over the result of the quick poll
 
2. **Start the course with the poll as an example of NoSQL application** (5 minutes)
   - Quickly go over the poll results
   - Raise the question: "What have happened"
   - Explain the dataflow of the poll application

3. **Discussion of NoSQL vs SQL with the poll as an example** (10 minutes)
   - Discuss the limitations of SQL databases in handling the poll data
   - Explain how NoSQL databases can address these limitations
   - Use the poll as a case study to illustrate the advantages of NoSQL systems
   - Invite audiences to think, why we start with sql, if nosql is so great?

4. **History of databases and the evolution of NoSQL** (15 minutes)
   - Discuss the history of databases, starting from pre-relational databases to the current NoSQL systems
   - Use the timeline diagram to illustrate the evolution of databases
   - Highlight key innovations that led to the development of NoSQL systems
   - Introduce the types of NoSQL databases:
     - Key-value stores (e.g., Redis)
     - Column-family stores (e.g., Cassandra)
     - Document stores (e.g., MongoDB)
     - Graph databases (e.g., Neo4j)
     - Others (e.g. Object databases, Vector databases)
   - Discuss the types of NoSQL databases and their use cases in bioinformatics and data science
     - 100,000 genomes project
5. **Wrap-up and quiz** (5 minutes)
   - Show decision tree and quadrant chart to summarize the types of NoSQL databases
   - Conduct a quick quiz to reinforce learning objectives
   - Provide resources for further reading and exploration of NoSQL databases

[^poll]: We build a quick poll hosted on github codespace to collect responses, and use it as an example of a NoSQL application. The lecturers will open [github repo](https://github.com/St-Jude-MS-ABDS/workshop-NoSQL) and run the main branch codespace. Open the codespace with the vscode webeditor, and run `cd 0-mock-session/poll && ./run.sh` to start the poll. The url and QR code will be displayed in the terminal. Participants can scan the QR code or open the URL to access the poll. 
# Lecturer's Notes

This section is for lecturers to remind themselves of what to do during the mock session.

## Diagrams
### Poll website architecture
```mermaid
%%{ init }%%
architecture-beta
    group webapp(cloud)[Poll App Architecture]

    service frontend(server)[Frontend Server] in webapp
    service backend(server)[Backend Server] in webapp
    service database(database)[Persistent Database] in webapp

    frontend:R -- L:backend
    backend:B -- T:database
```
### Poll workflow
```mermaid
sequenceDiagram
    participant Student as Participant
    participant Browser
    participant FastAPI_Server as Codespace
    participant MongoDB as Atlas

    Student->>Browser: Selects options and clicks "Submit"
    Browser->>FastAPI_Server: POST /vote (form data with selected statements)
    FastAPI_Server->>MongoDB: Update poll document (append vote)
    MongoDB-->>FastAPI_Server: Acknowledged

    FastAPI_Server-->>Browser: Redirect to /results

    Browser->>FastAPI_Server: GET /results
    FastAPI_Server->>MongoDB: Aggregate vote counts
    MongoDB-->>FastAPI_Server: Aggregated results
    FastAPI_Server-->>Browser: Render results page
    Browser-->>Student: Show vote counts
```
### SQL database scheme: poll as an example
```mermaid
erDiagram
    QUESTIONS ||--o{ OPTIONS : has
    VOTES ||--o{ VOTE_OPTIONS : includes
    OPTIONS ||--o{ VOTE_OPTIONS : selected_in

    QUESTIONS {
        string id PK
        string question_text
    }

    OPTIONS {
        string id PK
        string question_id FK
        string option_text
    }

    VOTES {
        string vote_id PK
        datetime timestamp
    }

    VOTE_OPTIONS {
        string vote_id FK
        string option_id FK
    }
```

### NoSQL database scheme: Document: poll as an example
```mermaid
classDiagram
    class Poll {
        string id
        string question
        string[] options
        string[][] votes
    }
```

### NoSQL database scheme: Key-value: poll as an example
```mermaid
classDiagram
    class Poll1 {
        string question
        string[] options
        string[][] votes
    }
```
### Evolution of Databases
```mermaid
timeline
    title Database Innovations
    section Pre-relational (~1950s-1960s)
        Magnetic Disk : 1968 Hierarchical model (IBM IMS)
               : 1969 Network model (CODASYL).

    section Relational (~1970s-Now)
        Codd's Relational Model & HDD : 1974 IBM System R 
        : 1978 Oracle
        : 1980 Ingres
        : 1986 official SQL standard
        : 1989 Postgres
        : 1995 MySQL

    section Next Generation (~Late 2000s-Now)
        Cheap RAM & SSDs & Cloud
        : 2007 Neo4j
        : 2009 MongoDB
        : 2009 Redis

```

### Early Database Models: Hierarchical: poll as an example
```mermaid
graph TD
    Poll["Poll"]
    Question["Question Text"]
    Option1["Option A"]
    Option2["Option B"]
    Option3["Option C"]
    Votes["Votes"]
    Vote1["Vote 1"]
    Vote2["Vote 2"]
    
    Poll --> Question
    Poll --> Options
    Options --> Option1
    Options --> Option2
    Options --> Option3
    Poll --> Votes
    Votes --> Vote1
    Votes --> Vote2
```

### Early Database Models: Network: poll as an example
```mermaid
erDiagram
    POLL ||--o{ QUESTION : has
    QUESTION ||--|{ OPTION : contains
    POLL ||--o{ VOTE : records
    VOTE }|--|| OPTION : selected
```
### Decision Tree for NoSQL Database Selection
```mermaid
graph TD
    %% Define Styles
    style Q1 fill:#f9f,stroke:#333,stroke-width:2px
    style SQL fill:#ccf,stroke:#333,stroke-width:1px
    style Graph fill:#fcf,stroke:#333,stroke-width:1px
    style Document fill:#cfc,stroke:#333,stroke-width:1px
    style KeyValue fill:#ffc,stroke:#333,stroke-width:1px
    style WideColumn fill:#fcc,stroke:#333,stroke-width:1px

    %% Flowchart Logic
    Q1("Is data highly structured & needs strict consistency (ACID)?")

    Q1 -->|"Yes"| SQL[SQL Database]
    Q1 -->|"No / Flexible"| Q2("What is the primary data model?")

    Q2 -->|"Relationships are the focus<br/>(e.g., social networks)"| Graph[Graph Database]
    Q2 -->|"Self-contained documents<br/>(e.g., user profiles)"| Document[Document Database]
    Q2 -->|"Simple, fast key-to-value lookups<br/>(e.g., caching)"| KeyValue[Key-Value Database]
    Q2 -->|"Massive datasets with dynamic columns<br/>(e.g., IoT data)"| WideColumn[Wide-Column Store]

```
## Before going to the classroom
Ensure the following are ready:
- [ ] USB type-c hub with HDMI output
- [ ] Fully charged laptop, or with power adapter
- [ ] A **live** mongodb instance on atlas. Save the connection string in any way. I will call alias `demodburi` in my terminal and it comes to my clipboard
- [ ] Mongodb network allow `0.0.0.0/0`
- [ ] A github account with access to the [workshop-NoSQL](https://github.com/St-Jude-MS-ABDS/workshop-NoSQL) and still have quota on github codespace. the limit will be 60 hours per month

~~mapreduce~~

## In the classroom: preparation
- [ ] Connect the laptop to the projector using the USB type-c hub. Use the screen in Mirror mode.
- [ ] Open the [github repo](https://github.com/St-Jude-MS-ABDS/workshop-NoSQL), open the main branch codespace, put the **tab ONLY** in a new virtual desktop. Let's say, desktop 2. **Change port 8000 visibility to public**. The devcontainer.json will no longer be able to change the visibility. Change it manually under `ports` tab in the codespace. Right click port 8000 and select "Change visibility -> public".
- [ ] Open powerpoint slides in the codespace, and put it in a new virtual desktop. Let's say, desktop 3.
- [ ] Open terminal on mac. We will use it to source `demodburi`


