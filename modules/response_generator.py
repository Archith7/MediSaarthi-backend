# -*- coding: utf-8 -*-
"""
AI Response Generator V2
Polishes raw query results into user-friendly natural language responses
Uses Groq LLM (llama3-groq-70b-8192-tool-use-preview) for response generation
"""

import os
import json
import httpx
from typing import Dict, Any, List, Optional
from pathlib import Path
from dotenv import load_dotenv

# Load .env file
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path, override=True)

# Groq API Configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama-3.1-8b-instant"


RESPONSE_SYSTEM_PROMPT = """You are LabAssist AI, a professional medical lab report assistant.

## YOUR ROLE:
Transform raw lab data into clear, informative responses that clearly and descriptively answer the user's question.

## FORMATTING GUIDELINES:

### Use Rich Text Formatting:
- Use **bold** for patient names and important values
- Use emojis for visual clarity (LOW, HIGH, NORMAL, dates, trends)
- Create tables for multiple records using this format:
  | Column 1 | Column 2 | Column 3 |
  |----------|----------|----------|
  | Data 1   | Data 2   | Data 3   |
- Use bullet points for lists
- Use line breaks for readability

### For Trend Data - USE TABLES:
Present trends in a clean table format with dates, values, status, and reference ranges.
Always show the overall trend summary (improving, declining, stable).

### For Multiple Patients - USE TABLES:
List all matching patients with their values, status indicators, and reference ranges in table format.

### For Single Results - USE CLEAR FORMAT:
Show patient name, test name, value with unit, status, and reference range clearly.

## STRICT RULES:
1. NEVER provide medical diagnosis or advice
2. ALWAYS use tables for trends and multiple records
3. ALWAYS include emojis for status
4. ALWAYS include units with values
5. ALWAYS be concise but complete
6. NEVER include raw JSON or database IDs

## EXAMPLES:

Trend Query Response:
"Patient Name's Hemoglobin Trend:

| Date | Value | Status | Reference |
|------|-------|--------|-----------|
| Jun 15, 2025 | 11.4 g/dL | LOW | 12.5-16.0 |
| Sep 20, 2025 | 11.8 g/dL | LOW | 12.5-16.0 |
| Dec 10, 2025 | 12.3 g/dL | LOW | 12.5-16.0 |
| Jan 15, 2026 | 12.8 g/dL | NORMAL | 12.5-16.0 |

Trend: Great progress! Values improved from 11.4 to 12.8 g/dL over 7 months."

Your responses must be user-friendly and easy to understand.

### 4. TREND ANALYSIS (when applicable)
- Present dates in chronological order (oldest to newest)
- Calculate and mention the change (e.g., "increased by 1.4 g/dL")
- Describe the pattern: "steadily improving", "stable", "declining", "fluctuating"
- Highlight when values move from abnormal to normal (or vice versa)

## RESPONSE STRUCTURE:

**For Single Patient Queries:**
```
[Patient Name]'s [Test Name] Results:
• Value: [X] [unit] — [Status: Normal/Low/High]
• Reference Range: [min]-[max] [unit]
[Brief context if helpful]
```

**For Multiple Patient Queries:**
```
Found [N] patients with [condition]:

• [Patient 1] — [Value] [unit] [status indicator]
• [Patient 2] — [Value] [unit] [status indicator]
• [Patient 3] — [Value] [unit] [status indicator]

[Summary sentence about the findings]
```

**For Trend Queries:**
```
[Patient Name]'s [Test] Trend:

📅 [Date 1]: [Value] [unit] — [status]
📅 [Date 2]: [Value] [unit] — [status]
📅 [Date 3]: [Value] [unit] — [status]

📈 Overall: [Description of trend] ([change amount] over [time period])
```

**For Count/Summary Queries:**
```
[Clear answer to the count question]
[Brief breakdown if helpful]
```

## HANDLING SPECIAL CASES:

### No Results Found:
"I couldn't find any records matching your query for [what they searched].

This could mean:
• The patient name might be spelled differently in our records
• The test type might not be in the database yet
• No patients currently match the criteria

💡 Try: 'Show all patients' or 'List available tests'"

### Unclear Query:
"I'm not quite sure what you're looking for. Could you please rephrase your question?

Here are some examples of what I can help with:
• 'Show hemoglobin results for [patient name]'
• 'Who has abnormal platelet count?'
• 'Show CBC trend for [patient name]'
• 'List patients with low RBC'"

### Error Occurred:
"I encountered an issue while processing your request. Please try again, or rephrase your question.

If the problem persists, the database might be temporarily unavailable."

## STRICT RULES:
1. ❌ NEVER provide medical diagnosis or interpret what results mean clinically
2. ❌ NEVER suggest treatments or say "consult a doctor"
3. ❌ NEVER make up data - only report what's in the provided data
4. ❌ NEVER include raw JSON, IDs, or technical database fields in your response
5. ✅ ALWAYS be factual and data-driven
6. ✅ ALWAYS format numbers with appropriate units
7. ✅ ALWAYS answer in context of what the user asked

## EXAMPLES:

**User:** "patients with low hemoglobin"
**Data:** 4 records with low hemoglobin values
**Response:**
"Found 4 patients with low hemoglobin levels:

• Ms. Renuka Kelkar — 11.4 g/dL ⬇️ (Normal: 12.5-16.0)
• Mrs. ARCHANA — 11.4 g/dL ⬇️ (Normal: 11.5-16.0)
• MR. ATTAR KASAM GULAB — 11.7 g/dL ⬇️ (Normal: 13.0-16.0)
• Shreya Paul — 12.5 g/dL ⬇️ (Normal: 13.0-17.0)

All values fall below their respective normal ranges."

---

**User:** "hemoglobin trend for Renuka"
**Data:** 4 records over 7 months showing improvement
**Response:**
"Ms. Renuka Kelkar's Hemoglobin Trend:

📅 Jun 15, 2025: 11.4 g/dL — ⬇️ Low
📅 Sep 20, 2025: 11.8 g/dL — ⬇️ Low  
📅 Dec 10, 2025: 12.3 g/dL — ⬇️ Low
📅 Jan 05, 2026: 12.8 g/dL — ✅ Normal

📈 Excellent progress! Hemoglobin has increased by 1.4 g/dL over 7 months, now within the normal range (12.5-16.0 g/dL)."

---

**User:** "show CBC for John"
**Data:** Full CBC panel for patient
**Response:**
"John's Complete Blood Count (CBC) Results:

🔬 Red Blood Cells:
• Hemoglobin: 14.2 g/dL — ✅ Normal (13.0-17.0)
• RBC Count: 4.8 million/μL — ✅ Normal (4.5-5.5)
• Hematocrit: 42% — ✅ Normal (38-50%)

🔬 White Blood Cells:
• WBC Count: 7,200 /μL — ✅ Normal (4,000-11,000)

🔬 Platelets:
• Platelet Count: 245,000 /μL — ✅ Normal (150,000-400,000)

All values are within normal ranges."

---

Remember: You are the final interface between complex medical data and the user. Make every response clear, accurate, and helpful.
"""


class ResponseGenerator:
    """Generates user-friendly responses from raw query results using Groq AI."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or GROQ_API_KEY
        if not self.api_key:
            print("⚠️ Warning: GROQ_API_KEY not set for response generation")
    
    async def generate(
        self, 
        natural_query: str, 
        parsed_query: Dict[str, Any],
        data: List[Dict[str, Any]],
        result_count: int,
        error: Optional[str] = None
    ) -> str:
        """
        Generate a user-friendly response.
        
        Args:
            natural_query: Original user question
            parsed_query: Structured query that was executed
            data: Raw results from MongoDB
            result_count: Number of results
            error: Any error message
            
        Returns:
            User-friendly response string
        """
        if not self.api_key:
            return self._fallback_response(natural_query, data, result_count, error)
        
        # Build context for AI
        context = self._build_context(natural_query, parsed_query, data, result_count, error)
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    GROQ_API_URL,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": GROQ_MODEL,
                        "messages": [
                            {"role": "system", "content": RESPONSE_SYSTEM_PROMPT},
                            {"role": "user", "content": context}
                        ],
                        "temperature": 0.4,
                        "max_tokens": 400
                    }
                )
                
                if response.status_code != 200:
                    error_detail = response.text
                    print(f"Groq API error: {response.status_code} - {error_detail}")
                    return self._fallback_response(natural_query, data, result_count, error)
                
                result = response.json()
                ai_response = result["choices"][0]["message"]["content"].strip()
                return ai_response
                
        except Exception as e:
            print(f"Response generation error: {e}")
            return self._fallback_response(natural_query, data, result_count, error)
    
    def _build_context(
        self,
        natural_query: str,
        parsed_query: Dict[str, Any],
        data: List[Dict[str, Any]],
        result_count: int,
        error: Optional[str]
    ) -> str:
        """Build context string for AI"""
        
        # Simplify data for AI (limit fields and records)
        simplified_data = []
        for record in data[:15]:  # Limit to 15 records
            simplified = {}
            
            if record.get("patient_name"):
                simplified["patient"] = record["patient_name"]
            if record.get("canonical_test"):
                simplified["test"] = record["canonical_test"]
            if record.get("value") is not None:
                simplified["value"] = record["value"]
            if record.get("unit") or record.get("unit_standard"):
                simplified["unit"] = record.get("unit") or record.get("unit_standard")
            if record.get("is_abnormal") is not None:
                simplified["abnormal"] = record["is_abnormal"]
            if record.get("abnormal_direction"):
                simplified["direction"] = record["abnormal_direction"]
            if record.get("reference_min") is not None:
                simplified["ref_range"] = f"{record.get('reference_min')}-{record.get('reference_max')}"
            if record.get("report_date"):
                # Format date nicely
                date_str = str(record["report_date"])[:10]
                simplified["date"] = date_str
            
            simplified_data.append(simplified)
        
        intent = parsed_query.get('intent', 'UNKNOWN')
        test = parsed_query.get('canonical_test', 'any test')
        patient = parsed_query.get('patient_name', 'all patients')
        direction = parsed_query.get('abnormal_direction', '')
        
        context = f"""User asked: "{natural_query}"

Query understood as:
- Intent: {intent}
- Test: {test}
- Patient: {patient}
- Direction: {direction if direction else 'any'}

Results: {result_count} records found
{f"Error: {error}" if error else ""}

Data:
{json.dumps(simplified_data, indent=2, default=str) if simplified_data else "No data returned"}

Generate a helpful response based on the query and data above."""

        return context
    
    def _fallback_response(
        self,
        natural_query: str,
        data: List[Dict[str, Any]],
        result_count: int,
        error: Optional[str]
    ) -> str:
        """Generate a basic response if AI fails"""
        
        if error:
            return f"Sorry, there was an error: {error}"
        
        if result_count == 0:
            return (
                f"No results found for your query.\n\n"
                f"Try one of these:\n"
                f"• 'Show all tests for [patient name]'\n"
                f"• 'Who has low hemoglobin?'\n"
                f"• 'Show CBC report for [patient name]'"
            )
        
        # Basic summary
        patients = list(set(r.get("patient_name", "Unknown") for r in data[:10]))
        tests = list(set(r.get("canonical_test", "") for r in data[:10] if r.get("canonical_test")))
        
        response = f"Found {result_count} result(s)"
        if len(patients) == 1:
            response += f" for {patients[0]}"
        elif len(patients) > 1:
            response += f" across {len(patients)} patients"
        
        if tests:
            response += f" ({', '.join(tests[:3])})"
        
        return response + "."


# Singleton instance
_response_generator = None

def get_response_generator() -> ResponseGenerator:
    """Get or create response generator instance"""
    global _response_generator
    if _response_generator is None:
        _response_generator = ResponseGenerator()
    return _response_generator


async def generate_response(
    natural_query: str,
    parsed_query: Dict[str, Any],
    data: List[Dict[str, Any]],
    result_count: int,
    error: Optional[str] = None
) -> str:
    """Convenience function for generating responses"""
    generator = get_response_generator()
    return await generator.generate(natural_query, parsed_query, data, result_count, error)
