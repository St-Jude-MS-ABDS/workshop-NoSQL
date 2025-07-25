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
   - Briefly introduce the lecturers and the course objectives.
   - Quick poll to gauge participants' familiarity with database concepts. [^poll]
   
  

[^poll]: We build a quick poll hosted on github codespace to collect responses, and use it as an example of a NoSQL application. The lecturers will open [github repo](https://github.com/St-Jude-MS-ABDS/workshop-NoSQL) and run the main branch codespace. Open the codespace with the vscode webeditor, and run `cd 0-mock-session/poll && ./run.sh` to start the poll. The url and QR code will be displayed in the terminal. Participants can scan the QR code or open the URL to access the poll. 

# Lecturer's Notes

This section is for lecturers to remind themselves of what to do during the mock session.

## Before going to the classroom
Ensure the following are ready:
- [ ] USB type-c hub with HDMI output
- [ ] Fully charged laptop, or with power adapter
- [ ] A **live** mongodb instance on atlas. Save the connection string in any way. I will call alias `demodburi` in my terminal and it comes to my clipboard
- [ ] Mongodb network allow `0.0.0.0/0`

## In the classroom
- [ ] Connect the laptop to the projector using the USB type-c hub.
- [ ] Open the [github repo](https://github.com/St-Jude-MS-ABDS/workshop-NoSQL), open the main branch codespace, put the **tab ONLY** in a new virtual desktop.
