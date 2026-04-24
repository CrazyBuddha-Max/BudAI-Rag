# Introduction
This is the Rag Q&A system of BudAI's official AI product, which is divided into an AI dialogue system and a backend management system. Who is BudAI? Exactly below: smile:)
#Functional design
### The functions of the AI dialogue system include:
- Register
- Login
- Authentication (permissions are divided into regular users and VIP users)
- AI dialogue (each dialogue window has a window creation time)
- There is a chat history record, and each window can set the context length (in tokens). Users can choose the length range of the context based on the large model, as this method may cause the context truncation to be too rigid. Therefore, to determine whether the conversation is complete, only the complete questions and replies will be placed in the context, even if the token has not reached the upper limit
- You can view and select the knowledge base
- AI chat assistant can add, delete, modify and search. AI chat assistant can set parameters such as top-n, temperature, context length, recall rate, etc
- Personal account settings allow for modification of account information and account cancellation
### The functions of the management system include:
- User's additions, deletions, modifications, and queries
- View user's conversation records
- Addition, deletion, modification, and search of knowledge base
- File upload can be added, deleted, modified, and queried, and files can also be downloaded
- The addition, deletion, modification, and search of large models can also be done using third-party APIs
- File parsing, using embedding model parsing, slicing truncation using intelligent slicing of large models, and the ability to select a specified large model on the page
# Page design:
### Backend management system page:
home page
- Knowledge Base Management
- File management
- Model management
- User Management
- User Information
- User conversation history
### AI dialogue system page:
home page
- Q&A
- AI chat assistant
- Chat Window
- Historical records
- Personal settings
# Technology Stack
- Front end: React+Magicui
- Backend: Python+FastAPI+Langchain+Langgraph
- Database: MySQL, Elasticsearch
# Project Architecture
### Backend
Routers → only responsible for receiving requests, calling services, and returning responses

Services → Responsible only for business logic

Repositories → Only responsible for SQL

Models → just the mapping of database tables

Schemas → just data format definition

### Front end
# Local deployment
database
`mysql`：
```
CREATE DATABASE budai_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;  
```
`Elasticsearch`: (Docker One Click Deployment)
```
cd backend
```
```
docker-compose up -d
```