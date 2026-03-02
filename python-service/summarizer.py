from transformers import pipeline, AutoTokenizer
import torch


device = 0 if torch.cuda.is_available() else -1



AVAILABLE_MODELS = {
    "bart": {
        "name": "facebook/bart-large-cnn",
        "task": "summarization",
        "max_tokens": 900
    },
    "flan": {
        "name": "google/flan-t5-large",
        "task": "text2text-generation",
        "max_tokens": 450
    },
    "pegasus": {
        "name": "google/pegasus-xsum",
        "task": "summarization",
        "max_tokens": 900
    }
}

loaded_models = {}


def get_summarizer(model_key: str):
    if model_key not in AVAILABLE_MODELS:
        raise ValueError(f"Model '{model_key}' not supported.")

    if model_key not in loaded_models:
        config = AVAILABLE_MODELS[model_key]
        tokenizer = AutoTokenizer.from_pretrained(config["name"])

        loaded_models[model_key] = pipeline(
            config["task"],
            model=config["name"],
            tokenizer=tokenizer,
            device=device
        )

    return loaded_models[model_key]


def clean_transcript(text: str) -> str:
    seen = set()
    filtered = []

    for line in text.split("\n"):
        line = line.strip()
        if not line:
            continue
        if line in seen:
            continue
        seen.add(line)
        filtered.append(line)

    return "\n".join(filtered)


def chunk_text(text: str, tokenizer, max_tokens: int):
    tokens = tokenizer.encode(text)
    chunks = []

    for i in range(0, len(tokens), max_tokens):
        subset = tokens[i:i + max_tokens]
        chunk = tokenizer.decode(subset, skip_special_tokens=True)
        if chunk.strip():
            chunks.append(chunk)

    return chunks


def summarize_text(text: str, model_key: str = "bart") -> str:
    text = clean_transcript(text)

    if not text.strip():
        raise ValueError("Transcript empty after cleaning.")

    summarizer = get_summarizer(model_key)
    tokenizer = summarizer.tokenizer
    max_tokens = AVAILABLE_MODELS[model_key]["max_tokens"]

    chunks = chunk_text(text, tokenizer, max_tokens)

    if not chunks:
        raise ValueError("No valid chunks generated.")

    chunk_summaries = []

    for chunk in chunks:

        if model_key == "flan":
            prompt = f"Summarize clearly:\n{chunk}"
            output = summarizer(
                prompt,
                max_length=250,
                min_length=120,
                do_sample=False,
                no_repeat_ngram_size=3
            )
            chunk_summaries.append(output[0]["generated_text"])

        else:
            output = summarizer(
                chunk,
                max_length=250,
                min_length=120,
                do_sample=False,
                no_repeat_ngram_size=3
            )
            chunk_summaries.append(output[0]["summary_text"])

    combined_text = " ".join(chunk_summaries)

    combined_chunks = chunk_text(combined_text, tokenizer, max_tokens)

    final_summaries = []

    for chunk in combined_chunks:
        output = summarizer(
            chunk,
            max_length=300,
            min_length=150,
            do_sample=False,
            no_repeat_ngram_size=3
        )
        final_summaries.append(
            output[0].get("summary_text", output[0].get("generated_text"))
        )

    return " ".join(final_summaries)