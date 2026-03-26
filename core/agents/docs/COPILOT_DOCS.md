# Copilot Instructions — Documentation Agent

## ✅ Purpose
Creates **human-readable documents, summaries, flow diagrams, reports, and audit logs**.

---

## ✅ Responsibilities

### Core Functions
- **Summarize test results** from all agents (QA, Performance, Security, DevOps)
- **Generate defect analysis documents** with root cause analysis
- **Produce Test Insights Reports** with trends and patterns
- **Generate Blueprint-to-Documentation mapping** for traceability
- **Create Markdown/HTML/PDF exports** of test results
- **Document agent-to-agent interactions** and workflows
- **Generate test coverage + risk maps** with visualizations
- **Create flow diagrams** (Mermaid, PlantUML) from blueprints

### Supported Output Formats
- Markdown (.md)
- HTML
- PDF (via ReportLab)
- JSON (structured reports)
- Mermaid diagrams
- PlantUML diagrams

---

## ✅ What NOT to do

### ❌ FORBIDDEN Actions
- ❌ Do NOT invent test logic or results
- ❌ Do NOT alter blueprints or workflows
- ❌ Do NOT output unvalidated technical claims
- ❌ Do NOT make test decisions (read-only agent)
- ❌ Do NOT modify test data or evidence
- ❌ Do NOT create misleading visualizations
- ❌ Do NOT hardcode report templates
- ❌ Do NOT expose sensitive data in reports

---

## ✅ What Copilot Should Generate

### Modular Components
```python
# ✅ GOOD: Report generators
class ReportGenerator:
    def generate_test_summary(self, results: List[TestResult]) -> Report:
        """Generate executive test summary"""
        pass
    
    def generate_defect_analysis(self, defects: List[Defect]) -> Analysis:
        """Analyze defects with root cause"""
        pass
    
    def generate_coverage_report(self, coverage: CoverageData) -> Report:
        """Generate test coverage report"""
        pass
```

### Generate These Types of Code
- ✅ Markdown summary templates
- ✅ HTML report builders
- ✅ Flow diagram definitions (Mermaid)
- ✅ Structured test reports (JSON)
- ✅ Cross-agent event timelines
- ✅ Coverage visualizations
- ✅ Risk heat maps
- ✅ Trend analysis charts
- ✅ Blueprint documentation generators

---

## ✅ What Copilot Should NOT Generate

### ❌ AVOID These Patterns
```python
# ❌ BAD: Inventing test results
def generate_report():
    return f"All tests passed"  # Don't invent!

# ❌ BAD: Hardcoded templates
REPORT_HTML = """
<html>
  <!-- 1000 lines of hardcoded HTML -->
</html>
"""

# ❌ BAD: Altering data
def create_report(results):
    # Filter out failures to make report look better
    return [r for r in results if r.passed]  # DON'T!
```

---

## ✅ Tools Used

### Plugin-Based Tool Access
```python
# ✅ CORRECT: Load via plugin system
markdown_gen = self.plugins.load("markdown-generator")
pdf_gen = self.plugins.load("reportlab")
diagram_gen = self.plugins.load("mermaid")

# ❌ INCORRECT: Direct imports
from reportlab.lib import pdfgen  # DON'T
```

### Primary Tools
- **Markdown generators** - Structured Markdown creation
- **ReportLab** (via plugin) - PDF generation
- **Mermaid** (via plugin) - Flow diagrams
- **PlantUML** (via plugin) - UML diagrams
- **Chart.js** (via plugin) - Interactive charts
- **Jinja2** (via plugin) - Template rendering

---

## ✅ Blueprint-First Architecture

### Reading Documentation Blueprints
```yaml
# docs_test_report.blueprint.yaml
blueprint_id: "docs_report_001"
type: documentation
report_type: test_summary

data_sources:
  - agent: qa
    results_path: "results/qa/*"
  - agent: performance
    results_path: "results/performance/*"
  - agent: security
    results_path: "results/security/*"

sections:
  - name: executive_summary
    include:
      - total_tests
      - pass_rate
      - critical_failures
  
  - name: detailed_results
    group_by: agent
    include:
      - test_name
      - status
      - duration
      - error_details
  
  - name: defect_analysis
    include:
      - defect_count_by_severity
      - root_cause_categories
      - affected_components
  
  - name: coverage_analysis
    include:
      - code_coverage
      - feature_coverage
      - risk_coverage
  
  - name: trends
    time_range: 30_days
    metrics:
      - pass_rate_trend
      - execution_time_trend
      - defect_density_trend

output_formats:
  - markdown
  - html
  - pdf

visualizations:
  - type: pie_chart
    data: pass_fail_distribution
  - type: bar_chart
    data: defects_by_severity
  - type: line_chart
    data: pass_rate_trend
```

### Blueprint-Driven Documentation
```python
# ✅ CORRECT: Blueprint-driven report generation
blueprint = self.blueprint_loader.load("docs_report_001")

# Collect data from specified sources
data = {}
for source in blueprint.data_sources:
    results = self.collect_results(source.agent, source.results_path)
    data[source.agent] = results

# Generate sections based on blueprint
report = Report(title=f"Test Report - {blueprint.report_type}")

for section_spec in blueprint.sections:
    section = self.generate_section(section_spec, data)
    report.add_section(section)

# Generate visualizations
for viz_spec in blueprint.visualizations:
    viz = self.generate_visualization(viz_spec, data)
    report.add_visualization(viz)

# Export in specified formats
for format in blueprint.output_formats:
    exporter = self.get_exporter(format)
    exporter.export(report, f"report.{format}")
```

---

## ✅ Report Generation

### Executive Summary Generation
```python
class TestSummaryGenerator:
    def generate_executive_summary(
        self,
        test_results: List[TestResult]
    ) -> ExecutiveSummary:
        """Generate high-level summary for stakeholders"""
        
        total = len(test_results)
        passed = sum(1 for r in test_results if r.status == "PASS")
        failed = sum(1 for r in test_results if r.status == "FAIL")
        pass_rate = (passed / total * 100) if total > 0 else 0
        
        # Find critical failures
        critical_failures = [
            r for r in test_results 
            if r.status == "FAIL" and r.severity == "CRITICAL"
        ]
        
        # Calculate total execution time
        total_duration = sum(r.duration for r in test_results)
        
        return ExecutiveSummary(
            total_tests=total,
            passed=passed,
            failed=failed,
            pass_rate=pass_rate,
            critical_failures_count=len(critical_failures),
            total_execution_time=total_duration,
            critical_failures=critical_failures
        )
```

### Defect Analysis Report
```python
class DefectAnalyzer:
    def analyze_defects(
        self,
        defects: List[Defect]
    ) -> DefectAnalysis:
        """Analyze defect patterns and root causes"""
        
        # Group by severity
        by_severity = defaultdict(list)
        for defect in defects:
            by_severity[defect.severity].append(defect)
        
        # Group by component
        by_component = defaultdict(list)
        for defect in defects:
            by_component[defect.component].append(defect)
        
        # Categorize root causes (use LLM for analysis)
        root_causes = self._categorize_root_causes(defects)
        
        # Calculate defect density
        defect_density = self._calculate_defect_density(defects)
        
        return DefectAnalysis(
            total_defects=len(defects),
            by_severity=dict(by_severity),
            by_component=dict(by_component),
            root_cause_categories=root_causes,
            defect_density=defect_density,
            recommendations=self._generate_recommendations(defects)
        )
    
    def _categorize_root_causes(self, defects: List[Defect]) -> Dict[str, int]:
        """Use LLM to categorize defect root causes"""
        
        # Group similar error messages
        error_summaries = [d.error_message for d in defects]
        
        prompt = f"""
        Analyze these {len(defects)} defects and categorize their root causes:
        
        {json.dumps(error_summaries[:50], indent=2)}
        
        Provide categories like:
        - Code Logic Errors
        - Configuration Issues
        - Environment Problems
        - Data Issues
        - Integration Failures
        
        Return JSON with category counts.
        """
        
        # ✅ Use LLM adapter
        categories_json = self.llm_adapter.generate(
            prompt=prompt,
            provider="openai",
            temperature=0.3
        )
        
        return json.loads(categories_json)
```

---

## ✅ Visualization Generation

### Mermaid Diagram Generation
```python
class DiagramGenerator:
    def generate_flow_diagram(self, blueprint: Blueprint) -> str:
        """Generate Mermaid flow diagram from blueprint"""
        
        mermaid = "```mermaid\n"
        mermaid += "graph TD\n"
        
        for i, step in enumerate(blueprint.steps):
            node_id = f"step{i}"
            mermaid += f"    {node_id}[{step.name}]\n"
            
            if i > 0:
                prev_id = f"step{i-1}"
                mermaid += f"    {prev_id} --> {node_id}\n"
        
        mermaid += "```\n"
        return mermaid
    
    def generate_agent_interaction_diagram(
        self,
        interactions: List[AgentInteraction]
    ) -> str:
        """Generate sequence diagram of agent interactions"""
        
        mermaid = "```mermaid\n"
        mermaid += "sequenceDiagram\n"
        
        for interaction in interactions:
            mermaid += f"    {interaction.source}->>+{interaction.target}: {interaction.message}\n"
            if interaction.response:
                mermaid += f"    {interaction.target}-->>-{interaction.source}: {interaction.response}\n"
        
        mermaid += "```\n"
        return mermaid
```

### Coverage Visualization
```python
class CoverageVisualizer:
    def generate_coverage_heatmap(
        self,
        coverage_data: CoverageData
    ) -> dict:
        """Generate coverage heatmap data"""
        
        heatmap = []
        
        for module in coverage_data.modules:
            heatmap.append({
                "module": module.name,
                "coverage": module.coverage_percent,
                "color": self._get_coverage_color(module.coverage_percent)
            })
        
        return {
            "type": "heatmap",
            "data": heatmap,
            "config": {
                "title": "Test Coverage by Module",
                "legend": {
                    "green": ">80% coverage",
                    "yellow": "50-80% coverage",
                    "red": "<50% coverage"
                }
            }
        }
    
    def _get_coverage_color(self, percent: float) -> str:
        if percent >= 80:
            return "green"
        elif percent >= 50:
            return "yellow"
        else:
            return "red"
```

---

## ✅ Markdown Report Generation

### Professional Markdown Report
```python
class MarkdownReportGenerator:
    def generate_test_report(
        self,
        summary: ExecutiveSummary,
        results: List[TestResult],
        defect_analysis: DefectAnalysis
    ) -> str:
        """Generate comprehensive Markdown test report"""
        
        md = "# Test Execution Report\n\n"
        
        # Executive Summary
        md += "## Executive Summary\n\n"
        md += f"- **Total Tests**: {summary.total_tests}\n"
        md += f"- **Passed**: ✅ {summary.passed}\n"
        md += f"- **Failed**: ❌ {summary.failed}\n"
        md += f"- **Pass Rate**: {summary.pass_rate:.1f}%\n"
        md += f"- **Execution Time**: {summary.total_execution_time:.2f}s\n"
        md += f"- **Critical Failures**: {summary.critical_failures_count}\n\n"
        
        # Pass Rate Progress Bar
        md += self._generate_progress_bar("Pass Rate", summary.pass_rate)
        md += "\n\n"
        
        # Detailed Results
        md += "## Detailed Test Results\n\n"
        md += "| Test Name | Agent | Status | Duration | Details |\n"
        md += "|-----------|-------|--------|----------|----------|\n"
        
        for result in results:
            emoji = "✅" if result.status == "PASS" else "❌"
            md += f"| {result.name} | {result.agent} | {emoji} {result.status} | {result.duration:.2f}s | [View]({result.url}) |\n"
        
        md += "\n"
        
        # Defect Analysis
        if defect_analysis.total_defects > 0:
            md += "## Defect Analysis\n\n"
            md += f"**Total Defects**: {defect_analysis.total_defects}\n\n"
            
            md += "### By Severity\n\n"
            for severity, defects in defect_analysis.by_severity.items():
                md += f"- **{severity}**: {len(defects)}\n"
            
            md += "\n### Root Cause Categories\n\n"
            for category, count in defect_analysis.root_cause_categories.items():
                md += f"- {category}: {count}\n"
            
            md += "\n### Recommendations\n\n"
            for rec in defect_analysis.recommendations:
                md += f"- {rec}\n"
        
        md += "\n---\n"
        md += f"*Report generated: {datetime.now().isoformat()}*\n"
        
        return md
    
    def _generate_progress_bar(self, label: str, percent: float, width: int = 20) -> str:
        """Generate ASCII progress bar"""
        filled = int(width * percent / 100)
        empty = width - filled
        bar = "█" * filled + "░" * empty
        return f"{label}: [{bar}] {percent:.1f}%"
```

---

## ✅ PDF Report Generation

### PDF Export
```python
class PDFReportGenerator:
    def export_to_pdf(self, report: Report, output_path: str):
        """Export report to PDF"""
        
        pdf_gen = self.plugins.load("reportlab")
        
        # Create PDF document
        doc = pdf_gen.create_document(output_path)
        
        # Add title page
        doc.add_title(report.title)
        doc.add_subtitle(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        
        # Add sections
        for section in report.sections:
            doc.add_heading(section.title, level=1)
            doc.add_paragraph(section.content)
            
            if section.table:
                doc.add_table(section.table)
            
            if section.chart:
                doc.add_chart(section.chart)
        
        # Save PDF
        doc.save()
```

---

## ✅ Code Generation Examples

### ✅ GOOD: Modular, Data-Driven
```python
class DocumentationAgent(BaseAgent):
    def __init__(self, runtime, llm_adapter, plugin_loader):
        super().__init__(runtime, llm_adapter, plugin_loader)
        self.summary_gen = TestSummaryGenerator()
        self.defect_analyzer = DefectAnalyzer(llm_adapter)
        self.diagram_gen = DiagramGenerator()
        self.markdown_gen = MarkdownReportGenerator()
    
    def generate_test_report(self, blueprint_id: str) -> Report:
        # Load blueprint
        blueprint = self.blueprint_loader.load(blueprint_id)
        
        # Collect results from all agents
        qa_results = self.collect_results("qa")
        perf_results = self.collect_results("performance")
        sec_results = self.collect_results("security")
        
        all_results = qa_results + perf_results + sec_results
        
        # Generate executive summary
        summary = self.summary_gen.generate_executive_summary(all_results)
        
        # Analyze defects
        defects = [r.defects for r in all_results if r.defects]
        defect_analysis = self.defect_analyzer.analyze_defects(defects)
        
        # Generate report
        markdown_report = self.markdown_gen.generate_test_report(
            summary=summary,
            results=all_results,
            defect_analysis=defect_analysis
        )
        
        # Export in requested formats
        for format in blueprint.output_formats:
            if format == "markdown":
                self.save_file(f"report.md", markdown_report)
            elif format == "pdf":
                self.pdf_gen.export_to_pdf(markdown_report, "report.pdf")
            elif format == "html":
                self.html_gen.export_to_html(markdown_report, "report.html")
        
        return Report(
            format="markdown",
            content=markdown_report,
            metadata={
                "total_tests": summary.total_tests,
                "pass_rate": summary.pass_rate
            }
        )
```

---

## ✅ File Structure

```
core/agents/docs/
├── __init__.py
├── agent.py                      # Main documentation agent
├── COPILOT_DOCS.md              # This file
├── config.py
├── generators/
│   ├── summary_generator.py     # Executive summaries
│   ├── markdown_generator.py    # Markdown reports
│   ├── pdf_generator.py         # PDF reports
│   └── html_generator.py        # HTML reports
├── analyzers/
│   ├── defect_analyzer.py       # Defect analysis
│   ├── trend_analyzer.py        # Trend analysis
│   └── coverage_analyzer.py     # Coverage analysis
├── visualizers/
│   ├── diagram_generator.py     # Mermaid/PlantUML
│   ├── chart_generator.py       # Charts and graphs
│   └── heatmap_generator.py     # Heatmaps
├── templates/
│   ├── markdown/
│   ├── html/
│   └── pdf/
└── tests/
    └── test_docs_agent.py
```

---

## ✅ Checklist for Documentation Agent Code

- [ ] Extends `BaseAgent` class
- [ ] Loads documentation blueprints
- [ ] Collects data from all agents
- [ ] Generates executive summaries
- [ ] Analyzes defects with LLM
- [ ] Creates visualizations
- [ ] Exports to multiple formats
- [ ] Never invents data
- [ ] Never alters source data
- [ ] Uses plugin loader for tools
- [ ] Uses LLM adapter for analysis
- [ ] Is read-only (no test modifications)
- [ ] Is modular (< 500 lines per file)

---

## 🎯 Remember

> **Document what happened, don't invent.**  
> **Visualize data, don't manipulate it.**  
> **Read-only agent, never modify test results.**

---

*Last updated: 2026-03-26*
