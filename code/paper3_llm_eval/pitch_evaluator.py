ASSESSMENT_CRITERIA = {
            "market_potential": {
                "name": "Market Potential",
                "questions": [
                    "Is there a clear, significant problem?",
                    "Is the market opportunity substantial?"
                ]
            },
            "solution_viability": {
                "name": "Solution Viability",
                "questions": [
                    "Does the solution make logical sense?",
                    "Is there potential for competitive advantage?"
                ]
            },
            "team_capability": {
                "name": "Team Capability",
                "questions": [
                    "Does the team have relevant expertise?",
                    "Do they demonstrate understanding of their market?"
                ]
            },
            "initial_traction": {
                "name": "Initial Traction",
                "questions": [
                    "Are there early signs of validation?",
                    "Do the metrics indicate potential?"
                ]
            }
        }

METHODOLOGY = """
# **Guidelines for One-Minute Startup Pitch Reviews**

## **Purpose**

The one-minute pitch is an initial screening tool to determine if a startup warrants further investigation in the due diligence stage. It is not meant to provide comprehensive details about all aspects of the business.

## **For Startup Founders**

Your one-minute pitch (approximately 150 words) should focus on:

### **Essential Elements**

1. #### Problem & Market Opportunity

* Clear statement of the problem you're solving  
* Target market size/opportunity

2. #### Solution & Innovation

* Your unique approach/solution  
* Key technological or business model innovation

3. #### Traction & Validation

* Current stage (MVP, beta, launched)  
* Key metrics (users, revenue, partnerships)

4. #### Team

* Relevant expertise and background  
* Why you're the right team to solve this problem

5. #### Ask

* Amount seeking  
* Primary use of funds

### **Tips for Success**

* Focus on compelling facts rather than general statements  
* Highlight what makes your solution unique  
* Include specific numbers when possible  
* Keep technical jargon to a minimum  
* Ensure audio quality and clear delivery

## **For Expert Reviewers**

The one-minute pitch should be evaluated based on:

### **Primary Assessment Criteria**

1. #### Market Potential

* Is there a clear, significant problem?  
* Is the market opportunity substantial?

2. #### Solution Viability

* Does the solution make logical sense?  
* Is there potential for competitive advantage?

3. #### Team Capability

* Does the team have relevant expertise?  
* Do they demonstrate understanding of their market?

4. #### Initial Traction

* Are there early signs of validation?  
* Do the metrics indicate potential?

### **Important Considerations**

* This is a screening tool, not comprehensive due diligence  
* Focus on potential and red flags rather than complete details  
* Save detailed questions for the due diligence stage  
* Consider whether the startup warrants further investigation

### **Rating Guide**

5: Strong potential across all criteria, clear candidate for due diligence 

4: Shows promise with some questions to explore in due diligence 

3: Mixed signals, requires significant clarification 

2: Significant concerns or gaps 

1: Not suitable for further consideration

## **Common Pitfalls to Avoid**

### **For Startups**

* Trying to cover too much information  
* Using vague or general statements  
* Focusing on features rather than value  
* Omitting key traction metrics

### **For Reviewers**

* Expecting full business plan details  
* Focusing too heavily on current limitations  
* Overlooking potential in favor of current state  
* Requiring detailed answers to all possible questions

## **Remember**

The goal is to identify promising opportunities that warrant further investigation, not to make final investment decisions at this stage


"""

import requests
import json
import os
from typing import Dict, Any

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")


def invoke_anthropic_api(prompt: str) -> str:
    """
    Invoke Anthropic's API directly for local testing.

    Reads ANTHROPIC_API_KEY from the environment at call time. Never
    embed keys in source — set them via shell or .env (see .env.template).
    """
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY environment variable not set")
    
    # Anthropic API endpoint
    api_url = "https://api.anthropic.com/v1/messages"
    
    # Prepare headers
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }
    
    # Prepare request body
    request_body = {
        "model": "claude-3-7-sonnet-20250219",
        "max_tokens": 2000,
        "temperature": 0.2,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ]
    }
    
    # Send request to API
    response = requests.post(
        api_url,
        headers=headers,
        json=request_body
    )
    
    # Check if request was successful
    if response.status_code != 200:
        error_message = f"API request failed with status code {response.status_code}: {response.text}"
        raise Exception(error_message)
    
    # Parse response
    response_data = response.json()
    return response_data["content"][0]["text"]

# Update the PitchReviewSystem class to include a local testing option
class PitchReviewSystem:
    def __init__(self, api_provider="anthropic", methodology=METHODOLOGY):
        self.api_provider = api_provider.lower()
        self.methodology = methodology

        # Validate API provider
        valid_providers = ["anthropic", "openai", "bedrock"]
        if self.api_provider not in valid_providers:
            raise ValueError(f"Invalid API provider: {api_provider}. Must be one of {valid_providers}")
        
        # Check if API key is set
        if self.api_provider == "anthropic" and ANTHROPIC_API_KEY is None:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")
        elif self.api_provider == "openai" and OPENAI_API_KEY is None:
            raise ValueError("OPENAI_API_KEY environment variable not set")

        self.assessment_criteria = {
            "market_potential": {
                "name": "Market Potential",
                "questions": [
                    "Is there a clear, significant problem?",
                    "Is the market opportunity substantial?"
                ]
            },
            "solution_viability": {
                "name": "Solution Viability",
                "questions": [
                    "Does the solution make logical sense?",
                    "Is there potential for competitive advantage?"
                ]
            },
            "team_capability": {
                "name": "Team Capability",
                "questions": [
                    "Does the team have relevant expertise?",
                    "Do they demonstrate understanding of their market?"
                ]
            },
            "initial_traction": {
                "name": "Initial Traction",
                "questions": [
                    "Are there early signs of validation?",
                    "Do the metrics indicate potential?"
                ]
            }
        }
    
    def evaluate_criteria(self, pitch_transcript: str, criteria_key: str) -> Dict[str, Any]:
        """Evaluate a specific criteria using the LLM"""
        criteria = self.assessment_criteria[criteria_key]

        print(f"Working on {criteria["name"]}")
        prompt = self._build_evaluation_prompt(
            pitch_transcript=pitch_transcript,
            criteria_name=criteria["name"],
            criteria_questions=criteria["questions"]
        )
        
        # Select the appropriate API based on provider
        if self.api_provider == "anthropic":
            response = invoke_anthropic_api(prompt)
        elif self.api_provider == "openai":
            response = invoke_openai_api(prompt)
        else:  # bedrock
            response = self._invoke_bedrock(prompt)
        
        # Parse the structured output from the LLM response
        try:
            # Find JSON in the response
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                json_str = response[json_start:json_end]
                parsed_response = json.loads(json_str)
                
                # Convert to our standard format
                standardized_response = {
                    "reasoning": parsed_response.get("reasoning_string", ""),
                    "suggestions": parsed_response.get("actionable_suggestions_string", ""),
                    "score": parsed_response.get("score_integer", 3),
                    "confidence": parsed_response.get("confidence_integer", 5)
                }
                return standardized_response
            else:
                return self._parse_unstructured_response(response)
        except json.JSONDecodeError:
            # Fallback parsing if not in perfect JSON format
            return self._parse_unstructured_response(response)
    
    def _build_evaluation_prompt(self, pitch_transcript: str, criteria_name: str, criteria_questions: list) -> str:
        """Build the prompt for evaluating a specific criteria"""
        questions_text = "\n".join([f"- {q}" for q in criteria_questions])
        
        prompt = f"""<role>
You are an venture scout workgin for an early stage venture fund and expert early stage (pre-seed, seed) startup pitch evaluator with extensive experience in venture capital and startup assessment.
</role>

<methodology>
You are following a structured review methodology to evaluate a one-minute startup pitch.
You will analyze only one specific criteria: {criteria_name}.
You will think step by step, analyze pros and cons, and assign a score from 1-5.

METHODOLOGY: {self.methodology}
</methodology>

<pitch transcript>
{pitch_transcript}
</pitch transcript>

<Primary Assessment Criteria to review>
{criteria_name}
SAMPLE QUESTIONS: {questions_text}
You may come up with additional questions.
</Primary Assessment Criteria to review>

<Chain of Thought>
First, I'll analyze what the pitch says about {criteria_name}.
Then, I'll identify the pros and cons related to this specific criteria.
I will reason step by step and write detailed analysis with pros and cons for {criteria_name}.
I will come up with short actionable suggestions to improve the score for {criteria_name}.

Based on the pros and cons and improvement suggestions, I'll assign a score based on the rating guide:
5: Strong potential, clear candidate for due diligence
4: Shows promise with some questions to explore
3: Mixed signals, requires significant clarification
2: Significant concerns or gaps
1: Not suitable for further consideration

Finally, I'll assess my confidence in this score on a scale of 1-10:
10: Extremely confident, with comprehensive information
7-9: Highly confident, with sufficient information
4-6: Moderately confident, but some ambiguity exists
1-3: Low confidence, significant information gaps
</Chain of Thought>

Please provide your evaluation in the following JSON format:
{{
  "reasoning_string": "Your detailed analysis with pros and cons",
  "actionable_suggestions_string": "Short actionable suggestions to improve the score.",
  "score_integer": X,
  "confidence_integer": Y
}}

Focus ONLY on {criteria_name} criteria in your evaluation.
"""
        return prompt

    def _invoke_bedrock(self, prompt: str) -> str:
        """Invoke AWS Bedrock to get a response from the LLM"""
        # This method would normally use the AWS Bedrock client
        # For local testing, we'll raise an exception if this is called
        # if self.use_local_api:
        #     raise RuntimeError("_invoke_bedrock called when use_local_api=True")
        
        # Initialize AWS Bedrock client if needed
        import boto3
        bedrock_runtime = boto3.client(
            service_name="bedrock-runtime",
            region_name=os.environ.get("AWS_REGION", "us-east-1")
        )
        
        request_body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 2000,
            "temperature": 0.2,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }
        
        response = bedrock_runtime.invoke_model(
            modelId="anthropic.claude-3-7-sonnet-20250219",
            body=json.dumps(request_body)
        )
        
        response_body = json.loads(response["body"].read())
        return response_body["content"][0]["text"]
    
    def _parse_unstructured_response(self, response: str) -> Dict[str, Any]:
        """Fallback method to parse unstructured response"""
        # Default values
        score = 3  # Default score
        confidence = 5  # Default confidence (medium)
        reasoning = ""
        suggestions = ""
        
        # Split response into sections
        sections = response.split("\n\n")
        
        # Try to identify reasoning and suggestions sections
        for i, section in enumerate(sections):
            if "analysis" in section.lower() or "pros and cons" in section.lower():
                reasoning = section
            elif "suggestion" in section.lower() or "improvement" in section.lower():
                suggestions = section
            elif "score" in section.lower() and ":" in section:
                try:
                    score_line = [line for line in section.split("\n") if "score" in line.lower() and ":" in line][0]
                    score = int(score_line.split(":")[1].strip().split()[0])
                except:
                    pass
            elif "confidence" in section.lower() and ":" in section:
                try:
                    confidence_line = [line for line in section.split("\n") if "confidence" in line.lower() and ":" in line][0]
                    confidence = int(confidence_line.split(":")[1].strip().split()[0])
                except:
                    pass
        
        # If we couldn't identify specific sections, use the whole response as reasoning
        if not reasoning:
            reasoning = response
                    
        return {
            "reasoning": reasoning,
            "suggestions": suggestions,
            "score": score,
            "confidence": confidence
        }
    
    def evaluate_pitch(self, pitch_transcript: str) -> Dict[str, Any]:
        """Evaluate a pitch across all criteria"""
        results = {}
        
        # Evaluate each criteria independently
        for criteria_key in self.assessment_criteria.keys():
            results[criteria_key] = self.evaluate_criteria(pitch_transcript, criteria_key)
        
        # Calculate overall score (average of all criteria scores)
        scores = [result["score"] for result in results.values()]
        overall_score = sum(scores) / len(scores)
        
        # Calculate average confidence
        confidences = [result.get("confidence", 5) for result in results.values()]
        overall_confidence = sum(confidences) / len(confidences)
        
        return {
            "criteria_evaluations": results,
            "overall_score": overall_score,
            "overall_confidence": overall_confidence,
            "recommendation": self._get_recommendation(overall_score)
        }
    
    def _get_recommendation(self, overall_score: float) -> str:
        """Get a recommendation based on the overall score"""
        if overall_score >= 4.5:
            return "Strong candidate for due diligence"
        elif overall_score >= 3.5:
            return "Promising candidate with specific questions to explore"
        elif overall_score >= 2.5:
            return "Requires significant clarification before proceeding"
        elif overall_score >= 1.5:
            return "Significant concerns or gaps; likely not a good fit"
        else:
            return "Not suitable for further consideration"

# Example usage
# if __name__ == "__main__":
#     import argparse
    
#     parser = argparse.ArgumentParser(description="Test the Pitch Review System locally using Anthropic API")
#     parser.add_argument("--pitch-file", required=True, help="Path to the file containing the pitch transcript")
    
#     args = parser.parse_args()

# Read the pitch transcript from file
def get_review(pitch_file):
    try:
        with open(pitch_file, 'r') as f:
            pitch_transcript = f.read()
    except FileNotFoundError:
        print(f"Error: File '{pitch_file}' not found")
        exit(1)

    # Evaluate the pitch using the local API
    print(f"Evaluating pitch {pitch_file} using Anthropic API...")

    # def __init__(self, api_provider="anthropic", methodology=""):
    # # Validate API provider
    # valid_providers = ["anthropic", "openai", "bedrock"]
    try:
        reviewer = PitchReviewSystem(api_provider="anthropic")
        evaluation_results = reviewer.evaluate_pitch(pitch_transcript)
        
        # Display results
        print("\n" + "="*50)
        print("PITCH EVALUATION RESULTS")
        print("="*50)
        
        criteria_evaluations = evaluation_results.get("criteria_evaluations", {})
        overall_score = evaluation_results.get("overall_score", 0)
        overall_confidence = evaluation_results.get("overall_confidence", 0)
        recommendation = evaluation_results.get("recommendation", "")
        
        # Display individual criteria evaluations
        for criteria_key, evaluation in criteria_evaluations.items():
            criteria_name = criteria_key.replace("_", " ").title()
            score = evaluation.get("score", 0)
            reasoning = evaluation.get("reasoning", "")
            
            print(f"\n{criteria_name} - Score: {score}/5")
            print("-"*50)
            print(reasoning)
        
        # Display overall results
        print("\n" + "="*50)
        print(f"OVERALL SCORE: {overall_score:.1f}/5")
        print(f"RECOMMENDATION: {recommendation}")
        print("="*50)

        # Create a dictionary
        # Specify the path for the JSON file
        json_file_name = os.path.splitext(os.path.basename(pitch_file))[0]
        json_file_path = f'pitch_reviews_anthropic_methodology/{json_file_name}.json'

        # Save the dictionary to a JSON file
        with open(json_file_path, 'w') as json_file:
            json.dump(evaluation_results, json_file, indent=4)  # 'indent=4' for pretty formatting

        print(f'Dictionary saved to {json_file_path}')


    except Exception as e:
        print(f"Error: {e}")
        exit(1)