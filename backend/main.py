import os
import re
from datetime import datetime
import sys
from flask import Flask, request, render_template
from job_searcher import JobSearcher
from vectorization import Vectorizer
from data_preprocess import preprocess, get_metadata

app = Flask(__name__, template_folder='../frontend')


def initialize_app():
    # Явная проверка на True/False
    if os.getenv('SKIP_INIT', '').lower() in ('true', '1', 'yes'):
        print("Skipping initialization as SKIP_INIT is set")
        return None, None

    try:
        print("Initializing vectorizer and search engine...")
        corpus = preprocess()
        if not corpus:
            raise ValueError("Empty corpus after preprocessing")

        tfidf_vectorizer = Vectorizer(corpus)
        tfidf_vectorizer.fit_corpus()
        tfidf_matrix = tfidf_vectorizer.transform()

        if tfidf_matrix is None:
            raise ValueError("TF-IDF matrix is None")

        search_engine = JobSearcher(tfidf_matrix.shape[1])
        metadata = get_metadata()
        search_engine.index_jobs(tfidf_matrix.toarray(), metadata)

        print("Initialization completed successfully!")
        return tfidf_vectorizer, search_engine

    except Exception as e:
        print(f"Initialization failed: {str(e)}", file=sys.stderr)
        raise  # Перебрасываем исключение дальше


tfidf_vectorizer, search_engine = initialize_app()


@app.route('/')
def home():
    return render_template('index.html')


@app.template_filter('datetimeformat')
def datetimeformat(value, format='%b %d, %Y'):
    if not value:
        return "No date"
    try:
        for fmt in ('%Y-%m-%d %H:%M:%S%z', '%Y-%m-%d', '%m/%d/%Y'):
            try:
                dt = datetime.strptime(value, fmt)
                return dt.strftime(format)
            except ValueError:
                continue
        return value
    except Exception:
        return value


def extract_skills_and_country(text):
    skills_pattern = r'Skills:\s*([A-Za-z].*?)(?=\s*Skills:|Country:|$)'
    skills_matches = re.findall(skills_pattern, text, re.DOTALL)

    skills = []
    for match in skills_matches:
        cleaned_skills = [s.strip() for s in re.split(r',\s+', match.replace('\n', ' ').replace('    ', ''))]
        skills.extend([s for s in cleaned_skills if s])

    skills = list(set(skills))

    return skills


@app.route('/search', methods=["POST"])
def search():
    description = request.form.get("description")
    if not description:
        return render_template('error.html', message="Description is empty"), 400

    try:
        description_vector = tfidf_vectorizer.transform(description=[description]).toarray().tolist()[0]
        ids = search_engine.search(description_vector)
        jobs = search_engine.fetch_metadata(ids)

        results = []
        for job in jobs:
            if len(job) > 3 and job[3] is not None:
                print(111)
                match = re.search(r'Posted On', job[3])
                print(match)
                if match is not None:
                    job_description = job[3][:match.span()[0]]
                    print(job_description, match.span()[0])
                else:
                    job_description = job[3]
            else:
                job_description = "No description available"
            result = {
                'title': job[1] if len(job) > 1 and job[1] is not None else "No title",
                'link': job[2] if len(job) > 2 and job[2] is not None else "#",
                'description': job_description,
                'published_date': job[4] if len(job) > 4 and job[4] is not None else "Date not specified",
                'is_hourly': job[5] if len(job) > 5 and job[5] is not None else "",
                'hourly_low': float(job[6]) if len(job) > 6 and job[6] is not None else 0.0,
                'hourly_high': float(job[7]) if len(job) > 7 and job[7] is not None else 0.0,
                'budget': float(job[8]) if len(job) > 8 and job[8] is not None else 0.0,
                'country': job[9] if len(job) > 9 and job[9] is not None else "Location not specified",
                'skills': extract_skills_and_country(job[3]) if len(job) > 3 and job[
                    3] is not None else "No skills specified"
            }
            results.append(result)
        return render_template('results.html',
                               query=description,
                               results=results,
                               count=len(results))

    except Exception as e:
        return render_template('error.html',
                               message=f"Search error: {str(e)}"), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)