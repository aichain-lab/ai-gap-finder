"""LLM prompts for gap analysis"""

GAP_ANALYSIS_PROMPT = """
You are a research assistant specializing in identifying gaps, limitations, and potential future research directions in scientific papers.

Given the following research paper details:
Title: {title}
Abstract: {abstract}
Field: {field}
{authors_info}

Please analyze this research and provide:

1. KEY FINDINGS: List 3-5 main findings or contributions from this work.

2. RESEARCH GAPS: Identify specific gaps in the research. For each gap, provide:
   - Gap description
   - Gap type (methodological, theoretical, empirical, technical, conceptual)
   - Confidence score (0.0-1.0)
   - Potential impact of addressing this gap

3. LIMITATIONS: List specific limitations mentioned or implied in the research.

4. METHODOLOGY GAPS: Identify gaps or issues in the research methodology.

5. SUGGESTED HYPOTHESES: Generate 2-3 novel research hypotheses based on the gaps identified. For each hypothesis:
   - The hypothesis statement
   - Rationale for the hypothesis
   - Feasibility score (0.0-1.0)
   - Required research methods

6. FUTURE DIRECTIONS: Suggest 3-5 concrete future research directions.

Format your response as valid JSON with the following structure:
{{
  "key_findings": ["finding1", "finding2", ...],
  "gaps": [
    {{
      "gap_description": "description",
      "confidence_score": 0.8,
      "gap_type": "methodological",
      "potential_impact": "impact description"
    }}
  ],
  "limitations": ["limitation1", "limitation2", ...],
  "methodology_gaps": ["gap1", "gap2", ...],
  "suggested_hypotheses": [
    {{
      "hypothesis": "hypothesis statement",
      "rationale": "rationale",
      "feasibility_score": 0.7,
      "required_methods": ["method1", "method2"]
    }}
  ],
  "future_directions": ["direction1", "direction2", ...]
}}

Be specific, actionable, and avoid generic statements. Focus on gaps that could lead to meaningful research contributions.
"""

TOPIC_ANALYSIS_PROMPT = """
You are analyzing multiple research papers on the topic: {topic} in the field of {field}.

Here are the papers to analyze:
{papers_info}

Please provide:

1. COMMON GAPS: Identify gaps that appear across multiple papers or are systematic in the field.

2. INDIVIDUAL PAPER GAPS: For each paper, identify specific gaps.

3. RESEARCH DIRECTIONS: Suggest overall research directions for this topic area.

Format your response as valid JSON:
{{
  "common_gaps": [
    {{
      "gap_description": "description",
      "confidence_score": 0.8,
      "gap_type": "systematic",
      "potential_impact": "field-wide impact"
    }}
  ],
  "individual_results": [
    {{
      "paper_title": "title",
      "gaps": [
        {{
          "gap_description": "description",
          "confidence_score": 0.7,
          "gap_type": "methodological",
          "potential_impact": "impact"
        }}
      ]
    }}
  ],
  "suggested_research_directions": ["direction1", "direction2", ...]
}}
"""

HYPOTHESIS_REFINEMENT_PROMPT = """
Given the research context and identified gaps, refine and expand the following hypotheses to make them more specific, testable, and impactful:

Research Context:
{context}

Identified Gaps:
{gaps}

Original Hypotheses:
{hypotheses}

Please refine each hypothesis to:
1. Make it more specific and testable
2. Align it better with the identified gaps
3. Suggest concrete experimental approaches
4. Assess feasibility realistically

Return refined hypotheses in JSON format with the same structure as the input.
"""
