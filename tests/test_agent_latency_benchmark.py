import time
import statistics
import json

from langchain_core.messages import HumanMessage

from app.GenAI.graph.consumer_agent_graph import consumer_graph
from app.GenAI.graph.rag_agent_graph import rag_graph
from app.GenAI.graph.chart_agent_graph import chart_graph
from app.GenAI.agents.forecast_agent import forecast_agent


CONSUMER_ID = "C001"
REPEAT_RUNS = 3


BENCHMARK_CASES = {
    "Consumer Agent": {
        "runner": consumer_graph,
        "message": (
            f"What is the consumption level of consumer {CONSUMER_ID}?"
        ),
    },
    "RAG Agent": {
        "runner": rag_graph,
        "message": (
            "How many working days does a domestic electricity "
            "connection take?"
        ),
    },
    "Chart Agent": {
        "runner": chart_graph,
        "message": (
            f"Prepare a chart of historical consumption "
            f"for consumer {CONSUMER_ID}."
        ),
    },
    "Forecast Agent": {
        "runner": forecast_agent,
        "message": (
            f"Forecast next month's consumption "
            f"for consumer {CONSUMER_ID}."
        ),
    },
}


def benchmark_agent(name, runner, message):
    print("\n" + "=" * 60)
    print(f"Agent: {name}")
    print(f"Request: {message}")

    timings = []

    for run_number in range(1, REPEAT_RUNS + 1):
        start_time = time.perf_counter()

        try:
            result = runner.invoke({
                "messages": [
                    HumanMessage(content=message)
                ]
            })

            elapsed = time.perf_counter() - start_time
            timings.append(elapsed)

            print(f"\nRun {run_number}: SUCCESS")
            print(f"Execution time: {elapsed:.3f} seconds")

            messages = result.get("messages", [])

            if messages:
                print("Final response:")
                print(messages[-1].content)

            if "chart_data" in result:
                print("Chart data:")
                print(
                    json.dumps(
                        result["chart_data"],
                        indent=2,
                        default=str
                    )
                )

        except Exception as error:
            elapsed = time.perf_counter() - start_time

            print(f"\nRun {run_number}: FAILED")
            print(f"Execution time: {elapsed:.3f} seconds")
            print(f"Error: {type(error).__name__}: {error}")

    print(f"\n{name} - Benchmark Summary")

    if timings:
        print(f"Successful runs: {len(timings)}/{REPEAT_RUNS}")
        print(f"First run: {timings[0]:.3f} seconds")

        if len(timings) > 1:
            repeat_average = statistics.mean(timings[1:])
            print(f"Repeat-run average: {repeat_average:.3f} seconds")

        print(
            f"Overall average: "
            f"{statistics.mean(timings):.3f} seconds"
        )
    else:
        print("All benchmark runs failed.")


def main():
    print("AGENT LATENCY BENCHMARK")
    print(f"Runs per agent: {REPEAT_RUNS}")

    for name, case in BENCHMARK_CASES.items():
        benchmark_agent(
            name=name,
            runner=case["runner"],
            message=case["message"],
        )


if __name__ == "__main__":
    main()
