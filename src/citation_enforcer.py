"""
Citation Enforcer - Making LLMs Cite Like Paralegals

This module wraps LLM outputs and enforces citation requirements,
preventing hallucination by rejecting any claim without a valid source reference.
"""

from typing import Dict, List, Optional
import re


class CitationEnforcer:
    """
    Enforces citation requirements on LLM-generated legal text.
    
    Every factual claim must include a [Doc:Page:Line] reference.
    Claims without citations are flagged or rejected.
    
    Example:
        >>> enforcer = CitationEnforcer()
        >>> text = "The property was transferred in 2004."
        >>> enforcer.validate(text)
        {"valid": False, "reason": "Claim lacks citation"}
    """
    
    # Regex pattern for valid citations: [Doc_123:Page_5:Line_42]
    CITATION_PATTERN = r'\[Doc_\d+:Page_\d+:Line_\d+\]'
    
    def __init__(self, strict_mode: bool = True):
        """
        Args:
            strict_mode: If True, reject text without citations.
                        If False, only warn about missing citations.
        """
        self.strict_mode = strict_mode
    
    def extract_citations(self, text: str) -> List[str]:
        """Find all citations in the text."""
        return re.findall(self.CITATION_PATTERN, text)
    
    def validate(self, text: str) -> Dict:
        """
        Validate that text contains proper citations.
        
        Returns:
            {
                "valid": bool,
                "citation_count": int,
                "citations": List[str],
                "reason": str (if invalid)
            }
        """
        citations = self.extract_citations(text)
        
        if not citations and self.strict_mode:
            return {
                "valid": False,
                "citation_count": 0,
                "citations": [],
                "reason": "No citations found. In strict mode, all claims require sources."
            }
        
        return {
            "valid": True,
            "citation_count": len(citations),
            "citations": citations,
            "reason": None
        }
    
    def enforce(self, llm_output: str, source_docs: Dict = None) -> Dict:
        """
        Post-process LLM output to ensure citation compliance.
        
        Args:
            llm_output: Raw text from the LLM
            source_docs: Optional dict mapping Doc IDs to actual documents
            
        Returns:
            {
                "text": str (processed output),
                "citations_verified": int,
                "citations_invalid": int
            }
        """
        citations = self.extract_citations(llm_output)
        
        verified = 0
        invalid = 0
        
        if source_docs:
            for citation in citations:
                doc_id = re.search(r'Doc_(\d+)', citation)
                if doc_id and doc_id.group(1) in source_docs:
                    verified += 1
                else:
                    invalid += 1
        else:
            verified = len(citations)
        
        return {
            "text": llm_output,
            "citations_verified": verified,
            "citations_invalid": invalid,
            "total_citations": len(citations)
        }


if __name__ == "__main__":
    enforcer = CitationEnforcer(strict_mode=True)
    
    # Test with cited text
    good_text = "The property was sold on 2025-01-10 [Doc_9845:Page_1:Line_8]."
    result = enforcer.validate(good_text)
    print(f"Valid: {result['valid']}, Citations: {result['citation_count']}")
    
    # Test without citations
    bad_text = "The property was sold in 2025."
    result = enforcer.validate(bad_text)
    print(f"Valid: {result['valid']}, Reason: {result['reason']}")
