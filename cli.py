#!/usr/bin/env python3
# /cli.py
# [Version 26-04-2025 15:28:13]

import os
import sys
import json
import argparse
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

from core.functions import ValidationAgent, AgentOrchestrator
from core.claude_integration import ClaudeAssessmentAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("verityai_cli.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("VerityAI.CLI")

def create_specialized_agent(agent_id: str, specialization: str) -> ValidationAgent:
    """Create a specialized validation agent"""
    return ValidationAgent(agent_id, specialization)

def run_assessment(system_id: str, evidence_path: str, output_dir: str) -> str:
    """Run a comprehensive assessment on an AI system"""
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Load evidence
    if not os.path.exists(evidence_path):
        logger.error(f"Evidence file not found: {evidence_path}")
        sys.exit(1)
    
    try:
        with open(evidence_path, 'r') as f:
            evidence = json.load(f)
    except json.JSONDecodeError:
        logger.error(f"Invalid JSON in evidence file: {evidence_path}")
        sys.exit(1)
    
    # Create orchestrator
    orchestrator = AgentOrchestrator()
    
    # Register specialized agents
    dimensions = [
        "transparency", "accountability", "fairness", 
        "privacy", "safety", "security", 
        "human_value", "social_impact"
    ]
    
    for dimension in dimensions:
        agent = create_specialized_agent(f"{dimension}_agent", dimension)
        orchestrator.register_agent(agent)
    
    # Create comprehensive assessment
    orchestration_id = orchestrator.create_comprehensive_assessment(system_id, {
        "evidence_path": evidence_path,
        "assessment_date": datetime.now().isoformat(),
        "evidence_metadata": evidence.get("metadata", {})
    })
    
    logger.info(f"Created assessment: {orchestration_id}")
    
    # Generate report
    report_json = orchestrator.generate_report(orchestration_id, "json")
    report_md = orchestrator.generate_report(orchestration_id, "markdown")
    
    # Save reports
    json_path = os.path.join(output_dir, f"{orchestration_id}.json")
    with open(json_path, 'w') as f:
        f.write(report_json)
    
    md_path = os.path.join(output_dir, f"{orchestration_id}.md")
    with open(md_path, 'w') as f:
        f.write(report_md)
    
    logger.info(f"Assessment completed. Reports saved to {output_dir}")
    
    return orchestration_id

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(description="VerityAI Assessment CLI")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Run assessment command
    assess_parser = subparsers.add_parser("assess", help="Run a comprehensive assessment")
    assess_parser.add_argument("--system-id", required=True, help="ID of the AI system to assess")
    assess_parser.add_argument("--evidence", required=True, help="Path to evidence JSON file")
    assess_parser.add_argument("--output-dir", default="./results", help="Directory to save results")
    
    # Create agent command
    agent_parser = subparsers.add_parser("create-agent", help="Create a specialized agent")
    agent_parser.add_argument("--agent-id", required=True, help="ID for the new agent")
    agent_parser.add_argument("--specialization", required=True, help="Agent specialization")
    
    # Parse arguments
    args = parser.parse_args()
    
    if args.command == "assess":
        run_assessment(args.system_id, args.evidence, args.output_dir)
    elif args.command == "create-agent":
        agent = create_specialized_agent(args.agent_id, args.specialization)
        logger.info(f"Created agent {args.agent_id} with specialization {args.specialization}")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
