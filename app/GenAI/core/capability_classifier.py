
import re
from typing import Literal

Capability = Literal[
    "consumer",
    "rag",
    "chart",
    "forecast",
    "email",
    "word",
]


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
        r"\bconsumer history\b",
        r"\bhistory of consumer\b",
        r"\bconsumption history\b",
        r"\bhistorical consumption\b",
        r"\bhistorical records?\b",
    ]

    chart_patterns = [
        r"\bchart\b",
        r"\bgraph\b",
        r"\bplot\b",
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

    email_patterns = [
        r"\bemail\b",
        r"\be-mail\b",
        r"\bdraft an email\b",
        r"\bcompose an email\b",
        r"\bwrite an email\b",
        r"\bsend an email\b",
        r"\bemail the results\b",
        r"\bmail the results\b",
    ]

    word_patterns = [
        r"\bword document\b",
        r"\bword file\b",
        r"\bdocx\b",
        r"\bms word\b",
        r"\bmicrosoft word\b",
        r"\bcreate a document\b",
        r"\bgenerate a document\b",
        r"\bprepare a document\b",
        r"\bexport to word\b",
        r"\bdownloadable document\b",
    ]

    if any(re.search(pattern, text) for pattern in consumer_patterns):
        capabilities.append("consumer")

    if any(re.search(pattern, text) for pattern in chart_patterns):
        capabilities.append("chart")

    if any(re.search(pattern, text) for pattern in rag_patterns):
        capabilities.append("rag")

    if any(re.search(pattern, text) for pattern in forecast_patterns):
        capabilities.append("forecast")

    if any(re.search(pattern, text) for pattern in email_patterns):
        capabilities.append("email")

    if any(re.search(pattern, text) for pattern in word_patterns):
        capabilities.append("word")

    return capabilities
