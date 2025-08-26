# Job Search

A system that helps job seekers find relevant job vacancies based on their text descriptions.

**Value**  
Time-saving in finding suitable job vacancies.

**Target Audience**  
Job seekers without experience, students.

**ML Task**  
Job vacancy search by semantic similarity to text query (IR task).

**Attention**

Due to GitHub restrictions, it is not possible to download the original dataset. I took the dataset from the [link](https://www.kaggle.com/datasets/etietopabraham/jobs-raw-data). The dataset should be located in the 'data' folder and named job_postings.csv for proper operation

### Requirements
- Docker
- Docker Compose

### How to launch

1. Clone the repository:
```
git clone https://github.com/FaritSharafutdinov/job_search.git
```

```
cd job_search
```

2. Download [nltk_data](https://disk.yandex.ru/d/MVx5qCSVrmRGOw) and unzip it. (P.S. git hub doesn't support huge files)
   
3. Move the nltk_data folder to /job_search

4. Download [dataset](https://www.kaggle.com/datasets/asaniczka/upwork-job-postings-dataset-2024-50k-records) and create a /job_search/backend/job_dataset folder and put the dataset in it.

5. Run docker:
```
docker compose up -d
```
6. Check the docker job-search-flask logs until it appears:
   ```Initialization completed successfully!```
8. Open http://127.0.0.1:5001/
