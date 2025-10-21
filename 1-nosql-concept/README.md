# The course will be given in PowerPoint
# Introduction to NoSQL: Concepts
- [The course will be given in PowerPoint](#the-course-will-be-given-in-powerpoint)
- [Introduction to NoSQL: Concepts](#introduction-to-nosql-concepts)
  - [A brief history of database](#a-brief-history-of-database)
    - [pre-relational database](#pre-relational-database)
    - [Relational Era](#relational-era)
- [Reference](#reference)


## A brief history of database

What's a database?

> _database_ is an organized collection of data -- [wikipedia](https://en.wikipedia.org/wiki/Database)

In this definition, a book is a database, in physical form, and one of the earliest examples of a database. The book is organized in a way that allows you to find information quickly.


![Punch card and 1890 census](https://upload.wikimedia.org/wikipedia/commons/7/7c/1890_Census_Hollerith_Electrical_Counting_Machines_Sci_Amer.jpg)

> The Hollerith machine and the punch card system was one of the first examples of a digital/mechanical database. The machine was used to process the 1890 US Census, which was the first census to be conducted using a mechanical counting system. The punch card system allowed for the storage and retrieval of census data using mechanical counting machines.

The evolution of databases has been driven by the application demand and the storage media. 

```mermaid
timeline
    title Database Innovations Driven by Storage Eras

    section Pre-relational (~1950s-1960s)
        Magnetic Disk : 1968 Hierarchical model (IBM IMS)
               : 1969 Network model (CODASYL).

    section Relational (~1970s-Now)
        Codd's Relational Model : 1974 IBM System R 
        : 1978 Oracle
        : 1980 Ingres
        : 1986 official SQL standard
        : 1989 Postgres
        : 1995 MySQL

    section Next Generation (~Late 2000s-Now)
        Object Programming & Cloud : 2005 MapReduce
        : 2007 Neo4j
        : 2009 MongoDB
```
### pre-relational database

The emergence of the magnetic disk enabled the infrastructure of a database:
- You could now seek directly to a particular sector or block.
- This made random access feasible and efficient.
- It allowed databases to scale in complexity without sacrificing access speed.

Two dominant models emerged:
- Hierarchical model (IBM IMS)
- Network model (CODASYL)

Both models are "navigational" in nature, that is, you must navigate from one object to another using **explicitly defined** pointers.

```mermaid
---
title : Hierarchical model & Network model
---
graph TD
  subgraph Hierarchical model
    PROJ1[Project: RNA Folding] --> LEAD1[Lead: Alice]
    LEAD1 --> DEPT1[Department: CAB]
    LEAD1 --> EMAIL1[Email: alice@stjude.org]
    PROJ1 --> STOR1[Storage: /research/groups/alicegrp/projects/]
    STOR1 --> SIZE1[Size: 5.2 TB]
  end

  subgraph Network model
    PROJ2[Project: RNA Folding] --> LEAD2[Lead: Alice]
    STOR2[Storage: /research/groups/alicegrp/projects/] --> LEAD2

    LEAD2 --> DEPT2[Department: CAB]
    LEAD2 --> EMAIL2[Email: alice@stjude.org]
    STOR2 --> SIZE2[Size: 5.2 TB]
  end
```

The data schema was fixed in the pre-relational era.

### Relational Era
Edgar Codd published his relational database theory in paper "A Relational Model of Data for Large Shared Data Banks

| Concept | Description |
| ------- | ----------- |
| Table (Relation) | A set of rows and columns, like a spreadsheet. Each table represents an entity (e.g., User, Project). |
| Row (Tuple) | A single record in the table — a complete set of values for one entity instance. |
| Column (Attribute) | A field or property of the entity (e.g., name, email, size_tb). |
| Primary Key (PK) | A unique identifier for each row in a table. |
| Foreign Key (FK) | A reference to the primary key of another table — to link related data. |
| Normalization | A design process to eliminate redundancy and ensure data integrity. |

```mermaid
classDiagram
  class Project {
    +int project_id
    +string project_name
    +int lead_id
    +int storage_id
  }

  class Lead {
    +int lead_id
    +string name
    +string email
    +int department_id
  }

  class Department {
    +int department_id
    +string name
  }

  class Storage {
    +int storage_id
    +string path
    +float size_tb
  }

  Project --> Lead : belongs to
  Project --> Storage : uses
  Lead --> Department : works in

```

the relational database are normalized



# Reference
- Next Generation Databases: NoSQL, NewSQL, and Big Data. Guy Harrison, 2015