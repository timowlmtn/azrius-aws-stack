# azrius-analytics

## Video

https://youtu.be/C4dg8sVyFlk

## AWS

## Imagination in Action

### Firebase

We are using Firebase.

https://console.firebase.google.com/u/0/project/azrius-analytics-cc8a2/overview


### Old Stuff
## Basic


- https://modelcontextprotocol.io/quickstart/server
- https://github.com/aarora79/aws-cost-explorer-mcp-server/tree/main
- https://docs.anthropic.com/en/docs/agents-and-tools/claude-code/tutorials#set-up-model-context-protocol-mcp
- https://github.com/XGenerationLab/xiyan_mcp_server

## Prompts

- https://medium.com/datamindedbe/prompt-engineering-for-a-better-sql-code-generation-with-llms-263562c0c35d
- https://medium.com/%40machangsha/a-comprehensive-guidance-of-prompt-engineering-for-natural-language-to-sql-20d4c9dea080
- https://aws.amazon.com/blogs/machine-learning/best-practices-for-prompt-engineering-with-meta-llama-3-for-text-to-sql-use-cases/
- https://www.optimizesmart.com/ai-prompt-engineering-for-sql-generation-7-lessons-i-learned/7

## Retrieval Augmented Generation

- https://www.youtube.com/watch?v=T-D1OfcDW1M


-------

# Using AI and RAG to Supercharge My Job Search

## Introduction

They say that looking for a job is a full time job.  At least, I want my job 
search to be meaningful and interesting.

My goal is to automated and personalize my job search using AI, RAG, 
orchestration tools.

* Tech Stack 
  * Selenium for web scraping 
  * Python as the language workhorse 
  * LLMs (OpenAI and ClaudMCP)
  * Google Sheets for tracking my jobs
    * https://console.cloud.google.com/home/dashboard?inv=1&invt=AbtmRw&project=azrius-analytics
  * Dagster to orchestrate 
  * Finally, Slack to alert me across platforms

## Ingestion and Filtering

**Tools**: Selenium, AI, and Google Sheets 

* **Selenium** connects via a python/chrome plugin to automated LinkedIn search
* **LLM** parses the HTML and extracts
  * Company 
  * Position 
  * Job Description 
* **Score** job and reject jobs that don’t fit score
* **Storage**: Cleaned data push into a structured Google Sheet

## Resume and Cover Letter Generation

**Tools**: Python, LLM, RAG
* Script reads the sheet to get the next job 
* RAG agent pulls 
  * My existing resume as a base 
  * Job description as context
* Outputs 
  * Tailored resume 
  * Custom cover letter 
* Manual Step: Proofread/edit AI-generated content 
* Feedback loop: Store edits as a ruleset into the prompt restrictions to improve next run

## Automation and Scheduling

**Tools**: Dagster, Slack

* Dagster:  Handles orchestration
  * Runs job on a schedule so I have a job plan daily 
  * Trigger Linked search and AI processing 
  * Alerts me that I need to perform manual steps to review the AI results
  
* Slack Bot:  Notifies me when 
  * New jobs found 
  * Resume and cover are ready for review 
  * Manual step is pending (submitting on the job site)

## Lesson Learned / Challenges

* LLMs make a lot of mistakes and you need to check their work 
* Using an automated process takes the soul-crushing tedium out of the job search 
* Gives me a purpose and something interesting to work on 
* Rule generation is interesting and it remains to be seen how well AI will follow the rules

## Future Work

* I would like to integrate my google email into the system, so I can periodically check for acceptances and rejections to make jobs as rejected
* This could also help me to understand gaps in my resume if I’m rejected from a job I thought I was highly qualified
* Integration into slack (requires public URL) to allow me to drive the system with chat commands from any device


