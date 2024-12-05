from dataclasses import dataclass

@dataclass
class AnalysisCreation():
    analysis_name: str
    analyst_id: int
    details: dict
    status: str