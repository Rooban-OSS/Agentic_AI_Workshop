from flask import Flask, request, jsonify
from agents import CandidateDataParserAgent, TechnicalDepthEvaluatorAgent, CommunicationSkillsEvaluatorAgent, CulturalFitEvaluatorAgent, ScoringAndAggregationAgent
import os
import json

app = Flask(__name__)

# Initialize the parser and scoring agents
parser_agent = CandidateDataParserAgent()
scoring_agent = ScoringAndAggregationAgent()

@app.route('/parse_candidate', methods=['POST'])
def parse_candidate_data():
    """
    Endpoint to parse candidate data (resume, answers, GitHub URL).
    Expects a resume file (PDF/DOCX), answers (array of objects with text and type), and GitHub URL in the request.
    Returns structured JSON with parsed data.
    """
    try:
        # Check if required data is provided
        if 'resume' not in request.files or 'answers' not in request.form or 'github_url' not in request.form:
            return jsonify({"error": "Missing resume file, answers, or GitHub URL"}), 400

        resume_file = request.files['resume']
        answers = request.form['answers']
        github_url = request.form['github_url']

        try:
            # Parse answers as JSON array
            answers_array = json.loads(answers)
            if not isinstance(answers_array, list) or not all(isinstance(item, dict) and 'text' in item and 'type' in item for item in answers_array):
                return jsonify({"error": "Answers must be a JSON array of objects with 'text' and 'type' fields"}), 400
        except json.JSONDecodeError:
            return jsonify({"error": "Invalid JSON format for answers"}), 400

        # Save resume temporarily
        resume_path = f"temp_{resume_file.filename}"
        resume_file.save(resume_path)

        # Parse candidate data using the agent
        result = parser_agent.parse_candidate(resume_path, answers_array, github_url)

        # Clean up temporary file
        os.remove(resume_path)

        return jsonify(result), 200

    except Exception as e:
        if 'resume_path' in locals() and os.path.exists(resume_path):
            os.remove(resume_path)
        return jsonify({"error": str(e)}), 500

@app.route('/evaluate_candidate', methods=['POST'])
def evaluate_candidate_data():
    """
    Endpoint to evaluate candidate technical depth (resume, answers, GitHub URL, job description).
    Expects a resume file (PDF/DOCX), answers (array of objects with text and type), GitHub URL, and job description in the request.
    Returns structured JSON with evaluation results.
    """
    try:
        # Check if required data is provided
        if 'resume' not in request.files or 'answers' not in request.form or 'github_url' not in request.form or 'job_description' not in request.form:
            return jsonify({"error": "Missing resume file, answers, GitHub URL, or job description"}), 400

        resume_file = request.files['resume']
        answers = request.form['answers']
        github_url = request.form['github_url']
        job_description = request.form['job_description']

        try:
            # Parse answers as JSON array
            answers_array = json.loads(answers)
            if not isinstance(answers_array, list) or not all(isinstance(item, dict) and 'text' in item and 'type' in item for item in answers_array):
                return jsonify({"error": "Answers must be a JSON array of objects with 'text' and 'type' fields"}), 400
        except json.JSONDecodeError:
            return jsonify({"error": "Invalid JSON format for answers"}), 400

        # Save resume temporarily
        resume_path = f"temp_{resume_file.filename}"
        resume_file.save(resume_path)

        # Initialize the evaluator agent
        evaluator_agent = TechnicalDepthEvaluatorAgent()

        # Evaluate candidate data using the agent
        result = evaluator_agent.evaluate_candidate(resume_path, answers_array, github_url, job_description)

        # Clean up temporary file
        os.remove(resume_path)

        return jsonify(result), 200

    except Exception as e:
        if 'resume_path' in locals() and os.path.exists(resume_path):
            os.remove(resume_path)
        return jsonify({"error": str(e)}), 500

@app.route('/evaluate_cultural_fit', methods=['POST'])
def evaluate_cultural_fit():
    """
    Endpoint to evaluate candidate cultural fit (resume, answers, GitHub URL, job description).
    Expects a resume file (PDF/DOCX), answers (array of objects with text and type), GitHub URL, and job description in the request.
    Returns structured JSON with cultural fit evaluation results.
    """
    try:
        # Check if required data is provided
        if 'resume' not in request.files or 'answers' not in request.form or 'github_url' not in request.form or 'job_description' not in request.form:
            return jsonify({"error": "Missing resume file, answers, GitHub URL, or job description"}), 400

        resume_file = request.files['resume']
        answers = request.form['answers']
        github_url = request.form['github_url']
        job_description = request.form['job_description']

        try:
            # Parse answers as JSON array
            answers_array = json.loads(answers)
            if not isinstance(answers_array, list) or not all(isinstance(item, dict) and 'text' in item and 'type' in item for item in answers_array):
                return jsonify({"error": "Answers must be a JSON array of objects with 'text' and 'type' fields"}), 400
        except json.JSONDecodeError:
            return jsonify({"error": "Invalid JSON format for answers"}), 400

        # Save resume temporarily
        resume_path = f"temp_{resume_file.filename}"
        resume_file.save(resume_path)

        # Parse candidate data using the parser agent
        candidate_data = parser_agent.parse_candidate(resume_path, answers_array, github_url)
        if "error" in candidate_data:
            os.remove(resume_path)
            return jsonify({"error": f"Candidate parsing failed: {candidate_data['error']}"}), 500

        # Initialize the cultural fit evaluator agent
        cultural_evaluator = CulturalFitEvaluatorAgent()

        # Evaluate cultural fit
        result = cultural_evaluator.evaluate_cultural_fit(candidate_data, job_description)

        # Clean up temporary file
        os.remove(resume_path)

        return jsonify(result), 200

    except Exception as e:
        if 'resume_path' in locals() and os.path.exists(resume_path):
            os.remove(resume_path)
        return jsonify({"error": str(e)}), 500

@app.route('/aggregate_score', methods=['POST'])
def aggregate_score():
    """
    Endpoint to calculate aggregated candidate score based on evaluation results.
    Expects technical, communication, and cultural evaluation JSONs, and optional weights.
    Returns structured JSON with final score and breakdown.
    """
    try:
        # Check if required data is provided
        required_fields = ['technical_evaluation', 'communication_evaluation', 'cultural_evaluation']
        if not all(field in request.form for field in required_fields):
            return jsonify({"error": "Missing technical_evaluation, communication_evaluation, or cultural_evaluation"}), 400

        # Parse evaluation JSONs
        try:
            technical_evaluation = json.loads(request.form['technical_evaluation'])
            communication_evaluation = json.loads(request.form['communication_evaluation'])
            cultural_evaluation = json.loads(request.form['cultural_evaluation'])
        except json.JSONDecodeError:
            return jsonify({"error": "Invalid JSON format for evaluations"}), 400

        # Parse optional weights
        weights = None
        if 'weights' in request.form:
            try:
                weights = json.loads(request.form['weights'])
                if not isinstance(weights, dict) or not all(k in weights for k in ['technical', 'communication', 'cultural', 'optional']):
                    return jsonify({"error": "Weights must be a JSON object with technical, communication, cultural, and optional keys"}), 400
            except json.JSONDecodeError:
                return jsonify({"error": "Invalid JSON format for weights"}), 400

        # Calculate aggregated score
        result = scoring_agent.calculate_score(
            technical_evaluation=technical_evaluation,
            communication_evaluation=communication_evaluation,
            cultural_evaluation=cultural_evaluation,
            weights=weights
        )

        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)