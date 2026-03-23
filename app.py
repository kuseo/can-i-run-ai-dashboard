from __future__ import annotations

from typing import Any

import pandas as pd
import streamlit as st
from canirunai import CanIRunAI


st.set_page_config(page_title="Can I Run AI?", layout="wide")


@st.cache_resource(show_spinner="Loading canirunai SDK...")
def get_sdk() -> CanIRunAI:
    return CanIRunAI()


@st.cache_data(show_spinner="Preparing hardware and model catalogs...")
def prepare_catalogs() -> dict[str, list[dict[str, Any]]]:
    sdk = get_sdk()

    cpu_specs = sdk.list_specs("cpu")
    gpu_specs = sdk.list_specs("gpu")
    model_specs = sdk.list_specs("model")

    if not cpu_specs:
        cpu_specs = sdk.update_cpu().items
    if not gpu_specs:
        gpu_specs = sdk.update_gpu().items
    if not model_specs:
        model_specs = sdk.update_model().items

    return {
        "cpu": [spec.model_dump(mode="json") for spec in cpu_specs],
        "gpu": [spec.model_dump(mode="json") for spec in gpu_specs],
        "model": [spec.model_dump(mode="json") for spec in model_specs],
    }


@st.cache_data(show_spinner=False)
def run_check(cpu_names: tuple[str, ...], gpu_names: tuple[str, ...], memory_gb: float, model_name: str) -> dict[str, Any]:
    sdk = get_sdk()
    report = sdk.check(
        cpu_names=list(cpu_names),
        gpu_names=list(gpu_names),
        memory_gb=memory_gb,
        model_name=model_name,
    )
    return report.model_dump(mode="json")


def build_options(items: list[dict[str, Any]], secondary_fields: list[str]) -> list[dict[str, str]]:
    options: list[dict[str, str]] = []
    for item in items:
        details = [str(item.get(field)) for field in secondary_fields if item.get(field) not in (None, "", [])]
        label = item["canonical_name"]
        if details:
            label = f"{label} | {' | '.join(details)}"
        options.append({"label": label, "value": item["canonical_name"]})
    return options


def verdict_badge(verdict: str) -> str:
    palette = {
        "RUNS GREAT": ("#166534", "#dcfce7"),
        "RUNS WELL": ("#15803d", "#dcfce7"),
        "TIGHT FIT": ("#a16207", "#fef3c7"),
        "TOO HEAVY": ("#c2410c", "#ffedd5"),
        "IMPOSSIBLE": ("#b91c1c", "#fee2e2"),
    }
    text_color, bg_color = palette.get(verdict, ("#1f2937", "#e5e7eb"))
    return (
        f"<div style='display:inline-block;padding:0.6rem 0.9rem;border-radius:999px;"
        f"font-weight:700;color:{text_color};background:{bg_color};'>{verdict}</div>"
    )


def metric_card(label: str, value: str, *, tone: str = "neutral") -> str:
    tones = {
        "neutral": ("#111827", "#f3f4f6", "#d1d5db"),
        "green": ("#166534", "#dcfce7", "#86efac"),
        "yellow": ("#a16207", "#fef3c7", "#fcd34d"),
        "orange": ("#c2410c", "#ffedd5", "#fdba74"),
        "red": ("#b91c1c", "#fee2e2", "#fca5a5"),
    }
    text_color, bg_color, border_color = tones.get(tone, tones["neutral"])
    return f"""
    <div style="
        border: 1px solid {border_color};
        background: {bg_color};
        border-radius: 16px;
        padding: 1rem 1.1rem;
        min-height: 110px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    ">
        <div style="
            font-size: 0.85rem;
            font-weight: 600;
            color: #4b5563;
            margin-bottom: 0.5rem;
            text-transform: uppercase;
            letter-spacing: 0.04em;
        ">{label}</div>
        <div style="
            font-size: 1.5rem;
            font-weight: 800;
            color: {text_color};
            line-height: 1.2;
            word-break: break-word;
        ">{value}</div>
    </div>
    """


def verdict_tone(verdict: str) -> str:
    return {
        "RUNS GREAT": "green",
        "RUNS WELL": "green",
        "TIGHT FIT": "yellow",
        "TOO HEAVY": "orange",
        "IMPOSSIBLE": "red",
    }.get(verdict, "neutral")


def metric_table(report: dict[str, Any]) -> pd.DataFrame:
    placement = report["placement_estimate"]
    context = report["context_estimate"]
    throughput = report["throughput_estimate"]
    memory = report["wide"]["memory_estimate"]
    latency = report["wide"]["latency_estimate"]
    bottlenecks = report["wide"]["bottlenecks"]
    confidence = report["wide"]["confidence"]

    rows = [
        {"Category": "Summary", "Metric": "Verdict", "Value": report["verdict"]},
        {"Category": "Summary", "Metric": "Score", "Value": report["score"]},
        {"Category": "Placement", "Metric": "Mode", "Value": placement["mode"]},
        {"Category": "Placement", "Metric": "Single GPU Loadable", "Value": placement["single_gpu_loadable"]},
        {"Category": "Placement", "Metric": "Replica Count", "Value": placement["replica_count"]},
        {"Category": "Placement", "Metric": "Used GPUs", "Value": ", ".join(placement["used_gpu_canonical_names"])},
        {"Category": "Context", "Metric": "Safe Context Tokens", "Value": context["safe_context_tokens"]},
        {"Category": "Context", "Metric": "Max Context Tokens", "Value": context["max_supported_context_tokens"]},
        {"Category": "Throughput", "Metric": "Decode Tokens/s", "Value": throughput["decode_tokens_per_sec"]},
        {"Category": "Throughput", "Metric": "Prefill Tokens/s", "Value": throughput["prefill_tokens_per_sec"]},
        {"Category": "Memory", "Metric": "Weights VRAM (GB)", "Value": memory["weights_vram_gb"]},
        {"Category": "Memory", "Metric": "Runtime Overhead VRAM (GB)", "Value": memory["runtime_overhead_vram_gb"]},
        {"Category": "Memory", "Metric": "KV Cache per 1k Tokens (GB)", "Value": memory["kv_cache_gb_per_1k_tokens"]},
        {"Category": "Memory", "Metric": "Total VRAM at Safe Context (GB)", "Value": memory["total_vram_gb_at_safe_context"]},
        {"Category": "Memory", "Metric": "VRAM Headroom (GB)", "Value": memory["vram_headroom_gb"]},
        {"Category": "Memory", "Metric": "Host RAM Required (GB)", "Value": memory["host_ram_required_gb"]},
        {"Category": "Memory", "Metric": "Host RAM Headroom (GB)", "Value": memory["host_ram_headroom_gb"]},
        {"Category": "Latency", "Metric": "First Token ms per 1k Prompt Tokens", "Value": latency["first_token_ms_per_1k_prompt_tokens"]},
        {"Category": "Latency", "Metric": "Generation ms per 128 Output Tokens", "Value": latency["generation_ms_per_128_output_tokens"]},
        {"Category": "Bottlenecks", "Metric": "Primary", "Value": bottlenecks["primary"]},
        {"Category": "Bottlenecks", "Metric": "Secondary", "Value": bottlenecks["secondary"]},
        {"Category": "Confidence", "Metric": "Context", "Value": confidence["context"]},
        {"Category": "Confidence", "Metric": "Throughput", "Value": confidence["throughput"]},
    ]
    return pd.DataFrame(rows)


def spec_table(items: list[dict[str, Any]], columns: list[str]) -> pd.DataFrame:
    rows = []
    for item in items:
        row = {column: item.get(column) for column in columns}
        rows.append(row)
    return pd.DataFrame(rows)


def render_catalog_tab(title: str, items: list[dict[str, Any]], columns: list[str], key: str) -> None:
    preview = spec_table(items, columns)
    selection = st.dataframe(
        preview,
        use_container_width=True,
        hide_index=True,
        on_select="rerun",
        selection_mode="single-row",
        key=key,
    )

    selected_rows = selection.get("selection", {}).get("rows", []) if isinstance(selection, dict) else []
    if not selected_rows:
        st.caption(f"Select a {title} item to inspect detailed fields.")
        return

    selected_item = items[selected_rows[0]]
    st.markdown(f"**Selected {title}:** `{selected_item['canonical_name']}`")
    st.json(selected_item)


def render() -> None:
    st.title("Can I Run AI?")
    st.caption("Select hardware and a model. The dashboard runs `canirunai.check()` immediately when the inputs are complete.")

    catalogs = prepare_catalogs()

    cpu_options = build_options(catalogs["cpu"], ["vendor", "cores", "threads", "boost_clock_ghz"])
    gpu_options = build_options(catalogs["gpu"], ["vendor", "memory_size_gib", "memory_bandwidth_gbs"])
    model_options = build_options(catalogs["model"], ["task", "num_parameters", "declared_context_tokens"])

    cpu_label_map = {item["label"]: item["value"] for item in cpu_options}
    gpu_label_map = {item["label"]: item["value"] for item in gpu_options}
    model_label_map = {item["label"]: item["value"] for item in model_options}

    st.subheader("Inputs")
    col1, col2, col3, col4 = st.columns([1.2, 1.2, 1.4, 0.8])

    selected_cpu_labels = col1.multiselect("CPU", options=list(cpu_label_map), placeholder="Select one or more CPUs")
    selected_gpu_labels = col2.multiselect("GPU", options=list(gpu_label_map), placeholder="Select one or more GPUs")
    selected_model_label = col3.selectbox("Model", options=[""] + list(model_label_map), format_func=lambda value: value or "Select a model")
    memory_gb = col4.number_input("Memory (GB)", min_value=1.0, value=64.0, step=1.0)

    selected_cpus = tuple(cpu_label_map[label] for label in selected_cpu_labels)
    selected_gpus = tuple(gpu_label_map[label] for label in selected_gpu_labels)
    selected_model = model_label_map.get(selected_model_label, "")

    if not selected_cpus or not selected_gpus or not selected_model:
        st.info("Choose at least one CPU, one GPU, and one model to run the fit check.")
    else:
        report = run_check(selected_cpus, selected_gpus, float(memory_gb), selected_model)

        card1, card2, card3, card4 = st.columns(4)
        with card1:
            st.markdown(metric_card("Verdict", report["verdict"], tone=verdict_tone(report["verdict"])), unsafe_allow_html=True)
        with card2:
            st.markdown(metric_card("Score", str(report["score"])), unsafe_allow_html=True)
        with card3:
            st.markdown(
                metric_card("Safe Context", f'{report["context_estimate"]["safe_context_tokens"]:,}'),
                unsafe_allow_html=True,
            )
        with card4:
            st.markdown(
                metric_card("Decode Tokens/s", f'{report["throughput_estimate"]["decode_tokens_per_sec"]:.2f}'),
                unsafe_allow_html=True,
            )

        with st.expander("Check Result", expanded=False):
            st.dataframe(metric_table(report), use_container_width=True, hide_index=True)

            with st.expander("Raw JSON", expanded=False):
                st.json(report)

    st.subheader("Catalog Preview")
    tab_cpu, tab_gpu, tab_model = st.tabs(["CPU", "GPU", "Model"])

    with tab_cpu:
        render_catalog_tab("CPU", catalogs["cpu"], ["canonical_name", "vendor", "cores", "threads", "boost_clock_ghz"], "cpu_preview")
    with tab_gpu:
        render_catalog_tab("GPU", catalogs["gpu"], ["canonical_name", "vendor", "memory_size_gib", "memory_bandwidth_gbs"], "gpu_preview")
    with tab_model:
        render_catalog_tab(
            "Model",
            catalogs["model"],
            ["canonical_name", "hf_repo_id", "task", "num_parameters", "declared_context_tokens"],
            "model_preview",
        )


render()
