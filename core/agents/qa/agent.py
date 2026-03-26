"""
QA Agent - AI-powered test execution agent
"""

import asyncio
from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime
from playwright.async_api import async_playwright, Page, Browser, BrowserContext

from ..base import BaseAgent, AgentCapability, agent_registry
from ...blueprints.models import Blueprint, BlueprintStep, ProjectContext
from ...validation.engine import ValidationEngine, Evidence


class QAAgent(BaseAgent):
    """
    QA Agent - Execute UI tests using Playwright
    
    Features:
    - Execute blueprint steps
    - Capture evidence (screenshots, DOM, network)
    - Deterministic validation
    - Auto-healing with LLM (Phase 2)
    """
    
    def __init__(self, context: ProjectContext, headless: bool = True):
        super().__init__(context, agent_type="qa")
        
        self.headless = headless
        self.browser: Optional[Browser] = None
        self.browser_context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        
        # Validation engine
        self.validator = ValidationEngine()
        
        # Evidence collection
        self.current_evidence: Dict[str, Any] = {}
        self.screenshots: List[str] = []
    
    async def initialize(self):
        """Initialize Playwright browser"""
        self.logger.info("Initializing Playwright browser...")
        
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=self.headless)
        self.browser_context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080}
        )
        self.page = await self.browser_context.new_page()
        
        self.logger.info("Browser initialized successfully")
    
    async def execute_blueprint(self, blueprint: Blueprint) -> Dict[str, Any]:
        """
        Execute a blueprint
        
        Args:
            blueprint: Blueprint to execute
        
        Returns:
            Execution result with validation status
        """
        self.logger.info(f"Executing blueprint: {blueprint.metadata.name}")
        
        start_time = datetime.now()
        
        try:
            # Initialize browser if not already done
            if not self.page:
                await self.initialize()
            
            # Reset evidence
            self.current_evidence = {}
            self.screenshots = []
            
            # Execute setup steps
            if blueprint.setup:
                self.logger.info("Executing setup steps...")
                for step in blueprint.setup:
                    await self._execute_step(step)
            
            # Execute main steps
            self.logger.info(f"Executing {len(blueprint.steps)} main steps...")
            for idx, step in enumerate(blueprint.steps, 1):
                self.logger.info(f"Step {idx}/{len(blueprint.steps)}: {step.action}")
                await self._execute_step(step)
            
            # Collect final evidence
            await self._collect_evidence()
            
            # Execute teardown steps
            if blueprint.teardown:
                self.logger.info("Executing teardown steps...")
                for step in blueprint.teardown:
                    await self._execute_step(step)
            
            # Validate results
            evidence = Evidence(
                evidence_type='ui',
                timestamp=datetime.now(),
                data=self.current_evidence,
                screenshots=self.screenshots
            )
            
            validation_result = self.validator.validate(
                blueprint.type,
                blueprint.expected,
                evidence
            )
            
            # Calculate duration
            duration_ms = (datetime.now() - start_time).total_seconds() * 1000
            
            # Save result to database
            self.db.save_test_result(
                blueprint_id=blueprint.blueprint_id,
                status=validation_result.status.value,
                duration_ms=int(duration_ms),
                evidence=self.current_evidence,
                validation_result={
                    'passed_checks': validation_result.passed_checks,
                    'failed_checks': validation_result.failed_checks,
                    'errors': validation_result.errors
                }
            )
            
            self.logger.info(
                f"Blueprint execution complete: {validation_result.status.value.upper()} "
                f"({duration_ms:.0f}ms)"
            )
            
            return {
                'blueprint_id': blueprint.blueprint_id,
                'status': validation_result.status.value,
                'duration_ms': duration_ms,
                'validation': {
                    'passed': validation_result.passed_checks,
                    'failed': validation_result.failed_checks,
                    'errors': validation_result.errors
                },
                'evidence': self.current_evidence,
                'screenshots': self.screenshots
            }
            
        except Exception as e:
            self.logger.error(f"Blueprint execution failed: {e}")
            
            # Save error to database
            self.db.save_test_result(
                blueprint_id=blueprint.blueprint_id,
                status='error',
                duration_ms=int((datetime.now() - start_time).total_seconds() * 1000),
                evidence={'error': str(e)},
                validation_result={'errors': [str(e)]}
            )
            
            raise
    
    async def _execute_step(self, step: BlueprintStep):
        """Execute a single blueprint step"""
        action = step.action.lower()
        
        # Map actions to methods
        action_map = {
            'navigate': self._action_navigate,
            'click': self._action_click,
            'fill': self._action_fill,
            'select': self._action_select,
            'wait': self._action_wait,
            'assert': self._action_assert,
            'screenshot': self._action_screenshot,
            'hover': self._action_hover,
        }
        
        action_func = action_map.get(action)
        if not action_func:
            raise ValueError(f"Unknown action: {action}")
        
        await action_func(step)
        
        # Log execution
        self.log_execution(action, {
            'selector': step.selector,
            'value': step.value,
            'timeout': step.timeout
        })
    
    async def _action_navigate(self, step: BlueprintStep):
        """Navigate to URL"""
        await self.page.goto(step.target, timeout=step.timeout)
    
    async def _action_click(self, step: BlueprintStep):
        """Click element"""
        await self.page.click(step.selector, timeout=step.timeout)
    
    async def _action_fill(self, step: BlueprintStep):
        """Fill input field"""
        await self.page.fill(step.selector, step.value, timeout=step.timeout)
    
    async def _action_select(self, step: BlueprintStep):
        """Select dropdown option"""
        await self.page.select_option(step.selector, step.value, timeout=step.timeout)
    
    async def _action_wait(self, step: BlueprintStep):
        """Wait for element"""
        await self.page.wait_for_selector(step.selector, timeout=step.timeout)
    
    async def _action_assert(self, step: BlueprintStep):
        """Assert element state (collect evidence)"""
        element = await self.page.query_selector(step.selector)
        
        if not element:
            raise AssertionError(f"Element not found: {step.selector}")
        
        # Collect element data
        is_visible = await element.is_visible()
        text_content = await element.text_content()
        
        # Store in evidence
        if 'elements' not in self.current_evidence:
            self.current_evidence['elements'] = {}
        
        self.current_evidence['elements'][step.selector] = {
            'visible': is_visible,
            'text': text_content
        }
    
    async def _action_screenshot(self, step: BlueprintStep):
        """Take screenshot"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        screenshot_name = f"screenshot_{timestamp}.png"
        screenshot_path = self.context.snapshots_path / screenshot_name
        
        # Ensure directory exists
        screenshot_path.parent.mkdir(parents=True, exist_ok=True)
        
        await self.page.screenshot(path=str(screenshot_path))
        self.screenshots.append(str(screenshot_path))
    
    async def _action_hover(self, step: BlueprintStep):
        """Hover over element"""
        await self.page.hover(step.selector, timeout=step.timeout)
    
    async def _collect_evidence(self):
        """Collect final evidence from page"""
        # Get current URL
        self.current_evidence['url'] = self.page.url
        
        # Get page title
        self.current_evidence['title'] = await self.page.title()
        
        # Take final screenshot
        await self._action_screenshot(BlueprintStep(
            action='screenshot',
            target=None,
            selector=None
        ))
    
    async def cleanup(self):
        """Cleanup Playwright resources"""
        if self.page:
            await self.page.close()
        if self.browser_context:
            await self.browser_context.close()
        if self.browser:
            await self.browser.close()
        if hasattr(self, 'playwright'):
            await self.playwright.stop()
        
        super().cleanup()


# Register QA Agent
agent_registry.register(
    'qa',
    QAAgent,
    [
        AgentCapability(
            'ui_testing',
            'Execute UI tests using Playwright',
            required_tools=['playwright']
        ),
        AgentCapability(
            'screenshot_capture',
            'Capture screenshots during test execution',
            required_tools=['playwright']
        ),
        AgentCapability(
            'deterministic_validation',
            'Validate test results deterministically',
            required_tools=[]
        )
    ]
)
