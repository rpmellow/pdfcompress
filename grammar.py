from transformers import T5ForConditionalGeneration, T5Tokenizer

# Load the model once at startup
model = T5ForConditionalGeneration.from_pretrained("vennify/t5-base-grammar-correction")
tokenizer = T5Tokenizer.from_pretrained("vennify/t5-base-grammar-correction")

def correct_grammar(text: str) -> str:
    input_text = "grammar: " + text.strip()
    input_ids = tokenizer.encode(input_text, return_tensors="pt", max_length=512, truncation=True)

    outputs = model.generate(
        input_ids,
        max_length=128,
        num_beams=4,
        early_stopping=True
    )

    return tokenizer.decode(outputs[0], skip_special_tokens=True)
