import re
from typing import Literal

Capability = Literal["consumer", "rag", "chart", "forecast"]


def classify_capabilities(user_request: str) -> list[Capability]:
    text = user_request.lower()
    capabilities: list[Capability] = []

    consumer_patterns = [
        r"\bconsumer details?\b",
        r"\bconsumer profile\b",
        r"\bconsumer information\b",
        r"\bconsumption level\b",
        r"\bmonthly usage\b",
        r"\bmonthly consumption\b",
    ]

    chart_patterns = [
        r"\bchart\b",
        r"\bgraph\b",
        r"\bplot\b",
        r"\bhistorical records?\b",
        r"\bhistory of consumer\b",
        r"\bconsumer history\b",
        r"\bconsumption history\b",
        r"\bhistorical consumption\b",
        r"\bconsumption trends?\b",
        r"\bvisuali[sz]e\b",
        r"\btrend chart\b",
    ]

    rag_patterns = [
        r"\bpolicy\b",
        r"\bregulation\b",
        r"\belectricity rules\b",
    ]

    forecast_patterns = [
        r"\bforecast\b",
        r"\bpredict\b",
        r"\bfuture consumption\b",
    ]

    if any(re.search(pattern, text) for pattern in consumer_patterns):
        capabilities.append("consumer")

    if any(re.search(pattern, text) for pattern in chart_patterns):
        capabilities.append("chart")

    if any(re.search(pattern, text) for pattern in rag_patterns):
        capabilities.append("rag")

    if any(re.search(pattern, text) for pattern in forecast_patterns):
        capabilities.append("forecast")

    return capabilities