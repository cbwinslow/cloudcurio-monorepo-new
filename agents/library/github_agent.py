#!/usr/bin/env python3
"""GitHub Integration Agent - Manages GitHub repository operations and issue tracking.

This agent provides comprehensive GitHub integration capabilities for the democratic swarm,
enabling autonomous management of issues, pull requests, project boards, and repository operations.
"""

import json
import logging
import subprocess
import time
from typing import Dict, List, Any, Optional, Callable
from pathlib import Path
import os
import re

from base_agent import ToolBasedAgent


class GitHubAgent(ToolBasedAgent):
    """GitHub Integration Agent for repository and issue management."""

    def __init__(self, config_path: str = "agents_config.json"):
        """Initialize the GitHub Agent.

        Args:
            config_path: Path to agent configuration file
        """
        super().__init__("github_agent", config_path)
        self.logger = logging.getLogger(__name__)

        # GitHub configuration
        self.repo_owner = os.getenv('GITHUB_REPO_OWNER', 'cbwinslow')
        self.repo_name = os.getenv('GITHUB_REPO_NAME', 'jcsnotfunny')
        self.token = os.getenv('GITHUB_TOKEN') or os.getenv('GH_TOKEN')

        # Initialize domain confidence for GitHub operations
        self.confidence.domains['github_management'] = 0.9
        self.confidence.domains['issue_tracking'] = 0.9
        self.confidence.domains['project_management'] = 0.85
        self.confidence.update_overall_confidence()

        # Cache for GitHub data
        self.issues_cache: Dict[str, Any] = {}
        self.last_cache_update = 0
        self.cache_ttl = 300  # 5 minutes

        self.logger.info("GitHub Agent initialized")

    def get_github_issues(self, state: str = "open", labels: Optional[List[str]] = None,
                         assignee: Optional[str] = None, limit: int = 50) -> Dict[str, Any]:
        """Get GitHub issues with filtering options.

        Args:
            state: Issue state ('open', 'closed', 'all')
            labels: List of labels to filter by
            assignee: Assignee username to filter by
            limit: Maximum number of issues to return

        Returns:
            Dictionary containing issues and metadata
        """
        try:
            # Check cache first
            cache_key = f"{state}_{str(labels)}_{assignee}_{limit}"
            current_time = time.time()

            if (cache_key in self.issues_cache and
                current_time - self.last_cache_update < self.cache_ttl):
                return self.issues_cache[cache_key]

            # Build GitHub CLI command
            cmd = ['gh', 'issue', 'list',
                   '--repo', f'{self.repo_owner}/{self.repo_name}',
                   '--state', state,
                   '--limit', str(limit),
                   '--json', 'number,title,labels,assignees,state,createdAt,updatedAt,body']

            if labels:
                for label in labels:
                    cmd.extend(['--label', label])

            if assignee:
                cmd.extend(['--assignee', assignee])

            # Execute command
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if result.returncode == 0:
                issues = json.loads(result.stdout)
                metadata = {
                    'total_count': len(issues),
                    'filtered_by': {
                        'state': state,
                        'labels': labels,
                        'assignee': assignee,
                        'limit': limit
                    },
                    'timestamp': current_time
                }

                response = {
                    'issues': issues,
                    'metadata': metadata
                }

                # Cache result
                self.issues_cache[cache_key] = response
                self.last_cache_update = current_time

                self.logger.info(f"Retrieved {len(issues)} GitHub issues")
                return response
            else:
                error_msg = f"Failed to get GitHub issues: {result.stderr}"
                self.logger.error(error_msg)
                return {'error': error_msg, 'issues': []}

        except subprocess.TimeoutExpired:
            error_msg = "GitHub API request timed out"
            self.logger.error(error_msg)
            return {'error': error_msg, 'issues': []}
        except Exception as e:
            error_msg = f"Error retrieving GitHub issues: {e}"
            self.logger.error(error_msg)
            return {'error': error_msg, 'issues': []}

    def analyze_issue_content(self, issue_number: int) -> Dict[str, Any]:
        """Analyze the content and requirements of a specific GitHub issue.

        Args:
            issue_number: The issue number to analyze

        Returns:
            Analysis of the issue content and requirements
        """
        try:
            # Get issue details
            cmd = ['gh', 'issue', 'view', str(issue_number),
                   '--repo', f'{self.repo_owner}/{self.repo_name}',
                   '--json', 'number,title,labels,assignees,body,comments']

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if result.returncode == 0:
                issue_data = json.loads(result.stdout)

                # Analyze content
                analysis = self._analyze_issue_text(issue_data)

                # Extract requirements and tasks
                requirements = self._extract_requirements(issue_data)

                # Determine complexity and effort
                complexity_analysis = self._assess_complexity(issue_data, requirements)

                result = {
                    'issue_number': issue_number,
                    'title': issue_data.get('title', ''),
                    'analysis': analysis,
                    'requirements': requirements,
                    'complexity': complexity_analysis,
                    'labels': [label.get('name', '') for label in issue_data.get('labels', [])],
                    'assignees': [assignee.get('login', '') for assignee in issue_data.get('assignees', [])],
                    'comment_count': len(issue_data.get('comments', []))
                }

                self.logger.info(f"Analyzed issue #{issue_number}: {issue_data.get('title', '')}")
                return result
            else:
                error_msg = f"Failed to get issue details: {result.stderr}"
                self.logger.error(error_msg)
                return {'error': error_msg}

        except Exception as e:
            error_msg = f"Error analyzing issue #{issue_number}: {e}"
            self.logger.error(error_msg)
            return {'error': error_msg}

    def _analyze_issue_text(self, issue_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze the text content of an issue."""
        title = issue_data.get('title', '').lower()
        body = issue_data.get('body', '').lower()

        # Categorize issue type
        issue_types = {
            'bug': ['bug', 'fix', 'error', 'issue', 'problem'],
            'feature': ['feature', 'enhancement', 'add', 'implement', 'create'],
            'documentation': ['docs', 'documentation', 'readme', 'guide'],
            'testing': ['test', 'testing', 'spec', 'validation'],
            'refactor': ['refactor', 'cleanup', 'restructure'],
            'research': ['research', 'investigate', 'explore']
        }

        categories = []
        for category, keywords in issue_types.items():
            if any(keyword in title or keyword in body for keyword in keywords):
                categories.append(category)

        # Extract key terms and technologies
        tech_keywords = ['python', 'javascript', 'react', 'node', 'api', 'database',
                        'docker', 'kubernetes', 'aws', 'github', 'ci/cd', 'testing']

        technologies = [tech for tech in tech_keywords if tech in body]

        # Determine urgency
        urgency_indicators = ['urgent', 'critical', 'asap', 'emergency', 'blocking']
        urgency = 'high' if any(indicator in body for indicator in urgency_indicators) else 'normal'

        return {
            'categories': categories,
            'technologies': technologies,
            'urgency': urgency,
            'estimated_effort': self._estimate_effort(body),
            'requires_external_resources': any(word in body for word in ['api', 'external', 'third-party', 'integration'])
        }

    def _extract_requirements(self, issue_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract requirements and tasks from issue content."""
        body = issue_data.get('body', '')

        requirements = []

        # Look for numbered lists, bullet points, checkboxes
        lines = body.split('\n')

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Check for task indicators
            task_indicators = ['- [ ]', '- [x]', '1.', '2.', '3.', '*', '•', '-']

            is_task = any(line.startswith(indicator.rstrip()) for indicator in task_indicators)

            if is_task or any(keyword in line.lower() for keyword in
                            ['need', 'should', 'must', 'implement', 'create', 'add', 'fix']):
                # Clean up the requirement text
                clean_text = re.sub(r'^[-*•]\s*\[.\]\s*', '', line)  # Remove checkboxes
                clean_text = re.sub(r'^\d+\.\s*', '', clean_text)     # Remove numbering

                # Determine task type
                task_type = 'implementation'
                if any(word in clean_text.lower() for word in ['test', 'spec']):
                    task_type = 'testing'
                elif any(word in clean_text.lower() for word in ['docs', 'readme']):
                    task_type = 'documentation'
                elif any(word in clean_text.lower() for word in ['research', 'investigate']):
                    task_type = 'research'

                requirements.append({
                    'description': clean_text.strip(),
                    'type': task_type,
                    'completed': '[x]' in line or '[X]' in line,
                    'priority': 'high' if any(word in clean_text.lower() for word in
                                            ['urgent', 'critical', 'important']) else 'normal'
                })

        return requirements

    def _assess_complexity(self, issue_data: Dict[str, Any],
                          requirements: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Assess the complexity and effort required for an issue."""
        body = issue_data.get('body', '')
        labels = [label.get('name', '') for label in issue_data.get('labels', [])]

        # Base complexity score
        complexity_score = 1.0

        # Factors that increase complexity
        complexity_factors = {
            'multiple_requirements': len(requirements) > 3,
            'external_dependencies': any(req.get('requires_external_resources', False) for req in requirements),
            'testing_required': any('test' in req.get('description', '').lower() for req in requirements),
            'documentation_required': any('docs' in req.get('description', '').lower() for req in requirements),
            'research_required': any('research' in req.get('description', '').lower() for req in requirements),
            'high_priority': any(label.lower() in ['urgent', 'critical', 'high-priority'] for label in labels),
            'complex_keywords': any(word in body.lower() for word in
                                   ['complex', 'difficult', 'challenging', 'architectural', 'refactor'])
        }

        # Apply complexity multipliers
        for factor, applies in complexity_factors.items():
            if applies:
                if factor in ['multiple_requirements', 'external_dependencies', 'high_priority']:
                    complexity_score *= 1.5
                elif factor in ['testing_required', 'documentation_required']:
                    complexity_score *= 1.3
                elif factor == 'research_required':
                    complexity_score *= 1.8
                elif factor == 'complex_keywords':
                    complexity_score *= 1.4

        # Determine complexity level
        if complexity_score < 2.0:
            complexity_level = 'low'
            estimated_hours = 2
        elif complexity_score < 4.0:
            complexity_level = 'medium'
            estimated_hours = 8
        elif complexity_score < 6.0:
            complexity_level = 'high'
            estimated_hours = 24
        else:
            complexity_level = 'very_high'
            estimated_hours = 80

        return {
            'complexity_score': complexity_score,
            'complexity_level': complexity_level,
            'estimated_hours': estimated_hours,
            'factors': complexity_factors,
            'recommended_agents': self._recommend_agents_for_issue(requirements, labels)
        }

    def _estimate_effort(self, body: str) -> str:
        """Estimate the effort level from issue description."""
        body_lower = body.lower()

        if any(word in body_lower for word in ['quick', 'simple', 'small', 'minor']):
            return 'small'
        elif any(word in body_lower for word in ['medium', 'moderate', 'significant']):
            return 'medium'
        elif any(word in body_lower for word in ['large', 'major', 'complex', 'extensive']):
            return 'large'
        else:
            return 'medium'  # default

    def _recommend_agents_for_issue(self, requirements: List[Dict[str, Any]],
                                   labels: List[str]) -> List[str]:
        """Recommend which agents should work on this issue."""
        recommended_agents = []

        # Analyze requirements for agent recommendations
        has_testing = any('test' in req.get('description', '').lower() for req in requirements)
        has_docs = any('doc' in req.get('description', '').lower() for req in requirements)
        has_research = any('research' in req.get('description', '').lower() for req in requirements)
        has_implementation = any(req.get('type') == 'implementation' for req in requirements)

        if has_testing:
            recommended_agents.extend(['quality_assurance_agent'])
        if has_docs:
            recommended_agents.extend(['content_automation_agent'])
        if has_research:
            recommended_agents.extend(['data_analyst_agent'])
        if has_implementation:
            recommended_agents.extend(['swarm_orchestrator', 'resource_manager'])

        # Label-based recommendations
        label_mappings = {
            'bug': ['diagnostic_agent', 'quality_assurance_agent'],
            'feature': ['swarm_orchestrator', 'communication_liaison'],
            'enhancement': ['monitoring_overseer', 'data_analyst_agent'],
            'documentation': ['content_automation_agent'],
            'testing': ['quality_assurance_agent'],
            'security': ['security_agent']
        }

        for label in labels:
            label_lower = label.lower()
            for label_key, agents in label_mappings.items():
                if label_key in label_lower:
                    recommended_agents.extend(agents)

        # Remove duplicates and return
        return list(set(recommended_agents))

    def update_issue_status(self, issue_number: int, status_update: str,
                           add_labels: Optional[List[str]] = None,
                           assign_to: Optional[str] = None) -> Dict[str, Any]:
        """Update the status of a GitHub issue.

        Args:
            issue_number: The issue number to update
            status_update: Status update comment to add
            add_labels: Labels to add to the issue
            assign_to: Username to assign the issue to

        Returns:
            Result of the status update
        """
        try:
            # Add a comment with status update
            if status_update:
                cmd = ['gh', 'issue', 'comment', str(issue_number),
                       '--repo', f'{self.repo_owner}/{self.repo_name}',
                       '--body', status_update]

                result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                if result.returncode != 0:
                    return {'error': f'Failed to add comment: {result.stderr}'}

            # Add labels if specified
            if add_labels:
                for label in add_labels:
                    cmd = ['gh', 'issue', 'edit', str(issue_number),
                           '--repo', f'{self.repo_owner}/{self.repo_name}',
                           '--add-label', label]

                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                    if result.returncode != 0:
                        self.logger.warning(f'Failed to add label {label}: {result.stderr}')

            # Assign if specified
            if assign_to:
                cmd = ['gh', 'issue', 'edit', str(issue_number),
                       '--repo', f'{self.repo_owner}/{self.repo_name}',
                       '--assignee', assign_to]

                result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                if result.returncode != 0:
                    return {'error': f'Failed to assign issue: {result.stderr}'}

            self.logger.info(f"Updated issue #{issue_number} with status: {status_update}")
            return {
                'success': True,
                'issue_number': issue_number,
                'status_update': status_update,
                'labels_added': add_labels or [],
                'assigned_to': assign_to
            }

        except Exception as e:
            error_msg = f"Error updating issue #{issue_number}: {e}"
            self.logger.error(error_msg)
            return {'error': error_msg}

    def create_issue_summary_report(self, issues_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a comprehensive summary report of GitHub issues.

        Args:
            issues_data: Issues data from get_github_issues

        Returns:
            Comprehensive summary report
        """
        try:
            issues = issues_data.get('issues', [])

            # Categorize issues
            categories = {
                'bugs': [],
                'features': [],
                'documentation': [],
                'maintenance': [],
                'other': []
            }

            priority_levels = {'low': 0, 'normal': 0, 'high': 0, 'urgent': 0}
            label_distribution = {}
            assignee_workload = {}

            for issue in issues:
                # Categorize by labels and content
                labels = [label.get('name', '') for label in issue.get('labels', [])]
                title = issue.get('title', '').lower()
                body = issue.get('body', '').lower()

                category = 'other'
                if any(label.lower() in ['bug', 'fix', 'error'] for label in labels) or \
                   any(word in title for word in ['fix', 'bug', 'error']):
                    category = 'bugs'
                elif any(label.lower() in ['feature', 'enhancement'] for label in labels) or \
                     any(word in title for word in ['add', 'implement', 'feature']):
                    category = 'features'
                elif any(label.lower() in ['docs', 'documentation'] for label in labels) or \
                     any(word in body for word in ['readme', 'documentation']):
                    category = 'documentation'
                elif any(word in title for word in ['refactor', 'cleanup', 'maintenance']):
                    category = 'maintenance'

                categories[category].append(issue)

                # Priority analysis
                priority = 'normal'
                if any(label.lower() in ['urgent', 'critical', 'high-priority'] for label in labels):
                    priority = 'urgent'
                elif any(word in body for word in ['important', 'priority']):
                    priority = 'high'

                priority_levels[priority] += 1

                # Label distribution
                for label in labels:
                    label_distribution[label] = label_distribution.get(label, 0) + 1

                # Assignee workload
                assignees = [assignee.get('login', '') for assignee in issue.get('assignees', [])]
                for assignee in assignees:
                    assignee_workload[assignee] = assignee_workload.get(assignee, 0) + 1

            # Generate insights
            insights = []
            total_issues = len(issues)

            if priority_levels['urgent'] > 0:
                insights.append(f"{priority_levels['urgent']} urgent issues require immediate attention")

            if len(categories['bugs']) > total_issues * 0.3:
                insights.append("High proportion of bug reports indicates potential quality issues")

            if len([a for a in assignee_workload.values() if a > 5]) > 0:
                insights.append("Some team members have high issue loads - consider redistribution")

            report = {
                'summary': {
                    'total_issues': total_issues,
                    'categories': {cat: len(issues) for cat, issues in categories.items()},
                    'priority_distribution': priority_levels,
                    'top_labels': sorted(label_distribution.items(), key=lambda x: x[1], reverse=True)[:10],
                    'assignee_workload': assignee_workload
                },
                'insights': insights,
                'recommendations': self._generate_issue_recommendations(categories, priority_levels, assignee_workload),
                'generated_at': time.time()
            }

            self.logger.info(f"Generated issue summary report for {total_issues} issues")
            return report

        except Exception as e:
            error_msg = f"Error generating issue summary report: {e}"
            self.logger.error(error_msg)
            return {'error': error_msg}

    def _generate_issue_recommendations(self, categories: Dict[str, List],
                                       priorities: Dict[str, int],
                                       workloads: Dict[str, int]) -> List[str]:
        """Generate recommendations based on issue analysis."""
        recommendations = []

        # Priority recommendations
        if priorities.get('urgent', 0) > 0:
            recommendations.append("Focus on urgent issues first - allocate top talent to critical items")

        # Category recommendations
        if len(categories['bugs']) > len(categories['features']) * 2:
            recommendations.append("High bug-to-feature ratio suggests quality improvements needed")

        if len(categories['documentation']) < len(categories['features']) * 0.5:
            recommendations.append("Increase documentation efforts to match feature development")

        # Workload recommendations
        max_workload = max(workloads.values()) if workloads else 0
        if max_workload > 10:
            recommendations.append("Redistribute workload - some team members are overloaded")

        # General recommendations
        if len(categories['features']) > len(categories['bugs']):
            recommendations.append("Good balance of feature development and bug fixes")

        return recommendations
