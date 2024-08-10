# from transformers import MambaForCausalLM, AutoTokenizer

# model = MambaForCausalLM.from_pretrained("SpirinEgor/mamba-1.4b")
# tokenizer = AutoTokenizer.from_pretrained("SpirinEgor/mamba-1.4b")

# s = "Я очень люблю лимончелло"
# input_ids = tokenizer(s, return_tensors="pt")["input_ids"]

# output_ids = model.generate(input_ids, max_new_tokens=50, do_sample=True, top_p=0.95, top_k=50, repetition_penalty=1.1)
# print(tokenizer.decode(output_ids[0]))
# # <s> Я очень люблю лимончелло. Просто без ума от этого ликёра, но когда его много я себя не контролирую и начинаю пить всё что можно.</s>

# pip install 'git+https://github.com/huggingface/transformers.git'
# Use a pipeline as a high-level helper

