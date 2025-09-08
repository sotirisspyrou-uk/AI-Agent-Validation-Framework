# /core/functions.py
# [Version 26-04-2025 15:18:52]

import json
import os
import datetime
import logging
from typing import Dict, List, Any, Optional, Union

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("verityai_agent.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("VerityAI")

# Base paths
KNOWLEDGE_BASE_PATH = os.path.join(os.path.dirname(__file__), "../knowledge")
ASSESSMENT_PATH = os.path.join(os.path.dirname(__file__), "../assessments")
TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), "../templates")

# Ensure directories exist
for path in [KNOWLEDGE_BASE_PATH, ASSESSMENT_PATH, TEMPLATE_PATH]:
    os.makedirs(path, exist_ok=True)

class ValidationAgent:
    """Base class for all VerityAI validation agents"""
    
    def __init__(self, agent_id: str, specialization: str):
        self.agent_id = agent_id
        self.specialization = specialization
        self.knowledge = {}
        self.assessment_results = {}
        self.logger = logging.getLogger(f"VerityAI.{agent_id}")
        self.load_knowledge()
    
    def load_knowledge(self) -> None:
        """Load specialized knowledge for this agent"""
        knowledge_path = os.path.join(KNOWLEDGE_BASE_PATH, f"{self.specialization}.json")
        if os.path.exists(knowledge_path):
            try:
                with open(knowledge_path, 'r') as f:
                    self.knowledge = json.load(f)
                self.logger.info(f"Loaded knowledge base for {self.specialization}")
            except Exception as e:
                self.logger.error(f"Error loading knowledge: {str(e)}")
        else:
            self.logger.warning(f"No knowledge base found for {self.specialization}")
    
    def create_assessment(self, system_id: str, metadata: Dict[str, Any]) -> str:
        """Initialize a new assessment"""
        assessment_id = f"{system_id}_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        assessment = {
            "assessment_id": assessment_id,
            "system_id": system_id,
            "agent_id": self.agent_id,
            "specialization": self.specialization,
            "metadata": metadata,
            "created_at": datetime.datetime.now().isoformat(),
            "updated_at": datetime.datetime.now().isoformat(),
            "status": "initialized",
            "evidence": [],
            "findings": [],
            "risks": [],
            "recommendations": [],
            "compliance_score": None
        }
        
        # Save initial assessment
        assessment_path = os.path.join(ASSESSMENT_PATH, f"{assessment_id}.json")
        with open(assessment_path, 'w') as f:
            json.dump(assessment, f, indent=2)
        
        self.assessment_results[assessment_id] = assessment
        self.logger.info(f"Created assessment {assessment_id} for system {system_id}")
        
        return assessment_id
    
    def add_evidence(self, assessment_id: str, evidence: Dict[str, Any]) -> None:
        """Add evidence to an assessment"""
        if assessment_id not in self.assessment_results:
            self._load_assessment(assessment_id)
        
        evidence["timestamp"] = datetime.datetime.now().isoformat()
        self.assessment_results[assessment_id]["evidence"].append(evidence)
        self.assessment_results[assessment_id]["updated_at"] = datetime.datetime.now().isoformat()
        
        # Save updated assessment
        self._save_assessment(assessment_id)
        self.logger.info(f"Added evidence to assessment {assessment_id}")
    
    def add_finding(self, assessment_id: str, finding: Dict[str, Any]) -> None:
        """Add a finding to an assessment"""
        if assessment_id not in self.assessment_results:
            self._load_assessment(assessment_id)
        
        finding["timestamp"] = datetime.datetime.now().isoformat()
        self.assessment_results[assessment_id]["findings"].append(finding)
        self.assessment_results[assessment_id]["updated_at"] = datetime.datetime.now().isoformat()
        
        # Save updated assessment
        self._save_assessment(assessment_id)
        self.logger.info(f"Added finding to assessment {assessment_id}")
    
    def add_risk(self, assessment_id: str, risk: Dict[str, Any]) -> None:
        """Add a risk to an assessment"""
        if assessment_id not in self.assessment_results:
            self._load_assessment(assessment_id)
        
        risk["timestamp"] = datetime.datetime.now().isoformat()
        self.assessment_results[assessment_id]["risks"].append(risk)
        self.assessment_results[assessment_id]["updated_at"] = datetime.datetime.now().isoformat()
        
        # Save updated assessment
        self._save_assessment(assessment_id)
        self.logger.info(f"Added risk to assessment {assessment_id}")
    
    def add_recommendation(self, assessment_id: str, recommendation: Dict[str, Any]) -> None:
        """Add a recommendation to an assessment"""
        if assessment_id not in self.assessment_results:
            self._load_assessment(assessment_id)
        
        recommendation["timestamp"] = datetime.datetime.now().isoformat()
        self.assessment_results[assessment_id]["recommendations"].append(recommendation)
        self.assessment_results[assessment_id]["updated_at"] = datetime.datetime.now().isoformat()
        
        # Save updated assessment
        self._save_assessment(assessment_id)
        self.logger.info(f"Added recommendation to assessment {assessment_id}")
    
    def set_compliance_score(self, assessment_id: str, score: float, dimension: str) -> None:
        """Set compliance score for a specific dimension"""
        if assessment_id not in self.assessment_results:
            self._load_assessment(assessment_id)
        
        if "compliance_scores" not in self.assessment_results[assessment_id]:
            self.assessment_results[assessment_id]["compliance_scores"] = {}
        
        self.assessment_results[assessment_id]["compliance_scores"][dimension] = score
        self.assessment_results[assessment_id]["updated_at"] = datetime.datetime.now().isoformat()
        
        # Calculate overall score if all dimensions are present
        dimensions = ["transparency", "accountability", "fairness", "privacy", 
                     "safety", "security", "human_value", "social_impact"]
        
        scores = self.assessment_results[assessment_id]["compliance_scores"]
        if all(dim in scores for dim in dimensions):
            overall_score = sum(scores.values()) / len(dimensions)
            self.assessment_results[assessment_id]["compliance_score"] = overall_score
        
        # Save updated assessment
        self._save_assessment(assessment_id)
        self.logger.info(f"Set compliance score for dimension {dimension} in assessment {assessment_id}")
    
    def finalize_assessment(self, assessment_id: str) -> Dict[str, Any]:
        """Finalize an assessment and return the results"""
        if assessment_id not in self.assessment_results:
            self._load_assessment(assessment_id)
        
        self.assessment_results[assessment_id]["status"] = "completed"
        self.assessment_results[assessment_id]["updated_at"] = datetime.datetime.now().isoformat()
        self.assessment_results[assessment_id]["completed_at"] = datetime.datetime.now().isoformat()
        
        # Save updated assessment
        self._save_assessment(assessment_id)
        self.logger.info(f"Finalized assessment {assessment_id}")
        
        return self.assessment_results[assessment_id]
    
    def _load_assessment(self, assessment_id: str) -> None:
        """Load an assessment from disk"""
        assessment_path = os.path.join(ASSESSMENT_PATH, f"{assessment_id}.json")
        if os.path.exists(assessment_path):
            try:
                with open(assessment_path, 'r') as f:
                    self.assessment_results[assessment_id] = json.load(f)
                self.logger.info(f"Loaded assessment {assessment_id}")
            except Exception as e:
                self.logger.error(f"Error loading assessment {assessment_id}: {str(e)}")
                raise ValueError(f"Could not load assessment {assessment_id}")
        else:
            self.logger.error(f"Assessment {assessment_id} not found")
            raise ValueError(f"Assessment {assessment_id} not found")
    
    def _save_assessment(self, assessment_id: str) -> None:
        """Save an assessment to disk"""
        assessment_path = os.path.join(ASSESSMENT_PATH, f"{assessment_id}.json")
        try:
            with open(assessment_path, 'w') as f:
                json.dump(self.assessment_results[assessment_id], f, indent=2)
            self.logger.info(f"Saved assessment {assessment_id}")
        except Exception as e:
            self.logger.error(f"Error saving assessment {assessment_id}: {str(e)}")
            raise ValueError(f"Could not save assessment {assessment_id}")


class AgentOrchestrator:
    """Coordinates multiple validation agents for comprehensive assessments"""
    
    def __init__(self):
        self.agents = {}
        self.assessments = {}
        self.logger = logging.getLogger("VerityAI.Orchestrator")
    
    def register_agent(self, agent: ValidationAgent) -> None:
        """Register a validation agent with the orchestrator"""
        self.agents[agent.agent_id] = agent
        self.logger.info(f"Registered agent {agent.agent_id} specializing in {agent.specialization}")
    
    def create_comprehensive_assessment(self, system_id: str, metadata: Dict[str, Any]) -> str:
        """Create a comprehensive assessment using all registered agents"""
        orchestration_id = f"orch_{system_id}_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        orchestration = {
            "orchestration_id": orchestration_id,
            "system_id": system_id,
            "metadata": metadata,
            "created_at": datetime.datetime.now().isoformat(),
            "updated_at": datetime.datetime.now().isoformat(),
            "status": "initialized",
            "agent_assessments": {},
            "integrated_findings": [],
            "integrated_risks": [],
            "integrated_recommendations": [],
            "compliance_scores": {},
            "overall_compliance_score": None
        }
        
        # Create individual assessments with each agent
        for agent_id, agent in self.agents.items():
            assessment_id = agent.create_assessment(system_id, metadata)
            orchestration["agent_assessments"][agent_id] = {
                "assessment_id": assessment_id,
                "specialization": agent.specialization,
                "status": "initialized"
            }
        
        # Save orchestration
        self.assessments[orchestration_id] = orchestration
        orchestration_path = os.path.join(ASSESSMENT_PATH, f"{orchestration_id}.json")
        with open(orchestration_path, 'w') as f:
            json.dump(orchestration, f, indent=2)
        
        self.logger.info(f"Created comprehensive assessment {orchestration_id} for system {system_id}")
        
        return orchestration_id
    
    def generate_report(self, orchestration_id: str, report_format: str = "json") -> str:
        """Generate a formatted report from assessment results"""
        if orchestration_id not in self.assessments:
            self._load_orchestration(orchestration_id)
        
        orchestration = self.assessments[orchestration_id]
        
        if report_format == "json":
            # Return the full orchestration as JSON
            return json.dumps(orchestration, indent=2)
        elif report_format == "markdown":
            # Generate a markdown report
            return self._generate_markdown_report(orchestration)
        else:
            raise ValueError(f"Unsupported report format: {report_format}")
    
    def _generate_markdown_report(self, orchestration: Dict[str, Any]) -> str:
        """Generate a markdown report from orchestration results"""
        system_id = orchestration["system_id"]
        report = []
        
        # Title
        report.append(f"# AI System Compliance Assessment: {system_id}")
        report.append(f"*Generated by VerityAI on {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
        report.append("")
        
        # Executive Summary
        report.append("## Executive Summary")
        report.append("")
        
        if "overall_compliance_score" in orchestration and orchestration["overall_compliance_score"] is not None:
            score = orchestration["overall_compliance_score"]
            report.append(f"**Overall Compliance Score:** {score:.2f}/5.0")
            
            # Simple rating
            if score >= 4.5:
                rating = "Excellent"
            elif score >= 4.0:
                rating = "Very Good"
            elif score >= 3.5:
                rating = "Good"
            elif score >= 3.0:
                rating = "Satisfactory"
            elif score >= 2.0:
                rating = "Needs Improvement"
            else:
                rating = "Significant Concerns"
            
            report.append(f"**Rating:** {rating}")
        
        report.append("")
        
        # Assessment Metadata
        report.append("## Assessment Information")
        report.append("")
        report.append(f"**Assessment ID:** {orchestration['orchestration_id']}")
        report.append(f"**System ID:** {orchestration['system_id']}")
        report.append(f"**Date Completed:** {orchestration.get('completed_at', 'N/A')}")
        report.append(f"**Conducted By:** VerityAI Assessment Platform")
        report.append("")
        
        # About VerityAI
        report.append("---")
        report.append("## About VerityAI")
        report.append("")
        report.append("VerityAI provides independent AI validation services to help organizations ensure their AI systems are compliant with regulatory requirements, industry standards, and ethical guidelines.")
        report.append("")
        report.append("For more information, visit [verityai.co](https://verityai.co).")
        
        return "\n".join(report)
    
    def _load_orchestration(self, orchestration_id: str) -> None:
        """Load an orchestration from disk"""
        orchestration_path = os.path.join(ASSESSMENT_PATH, f"{orchestration_id}.json")
        if os.path.exists(orchestration_path):
            try:
                with open(orchestration_path, 'r') as f:
                    self.assessments[orchestration_id] = json.load(f)
                self.logger.info(f"Loaded orchestration {orchestration_id}")
            except Exception as e:
                self.logger.error(f"Error loading orchestration {orchestration_id}: {str(e)}")
                raise ValueError(f"Could not load orchestration {orchestration_id}")
        else:
            self.logger.error(f"Orchestration {orchestration_id} not found")
            raise ValueError(f"Orchestration {orchestration_id} not found")
