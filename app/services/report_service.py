import os
from datetime import datetime

class ReportService:
    def __init__(self, output_dir: str = "reports"):
        self.output_dir = output_dir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

    def generate_executive_summary(self, analysis_results: str, chart_paths: list):
        """Generates a markdown report for the CDO."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = os.path.join(self.output_dir, f"Executive_Summary_{timestamp}.md")
        
        with open(report_path, "w") as f:
            f.write("# Autonomous Banking Analytics - Executive Summary\n")
            f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("## Analysis Results\n")
            f.write(analysis_results + "\n\n")
            f.write("## Visualizations\n")
            for path in chart_paths:
                f.write(f"![Chart]({os.path.abspath(path)})\n\n")
        
        return report_path
