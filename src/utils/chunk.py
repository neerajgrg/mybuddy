import os
import json
import tiktoken
import tqdm

# __script_dir = os.path.dirname(os.path.realpath(__file__))
# __base_dir = os.path.join(__script_dir, '..', '..')
# __content_file = os.path.join(__base_dir, 'build', 'product-help', 'experience-league-scraped.json')
# __output_dir = os.path.join(__base_dir, 'build', 'product-help')
# __output_file = os.path.join(__output_dir, 'experience-league-chunked.json')

__script_dir = os.path.dirname(os.path.realpath(__file__))
__base_dir = os.path.join(__script_dir, '..')
__content_file = os.path.join(__base_dir, 'data', 'test.json')
__output_dir = os.path.join(__base_dir, 'data')
__output_file = os.path.join(__output_dir, 'test-chunked.json')

print(__content_file)
print(__output_file)

__model_name = 'gpt-35-turbo'
__max_tokens_per_chunk = 1000
__sliding_window = 100


def encode(text: str, model_name: str):
    encoding = tiktoken.encoding_for_model(model_name)
    tokens = encoding.encode(text)
    return tokens


def decode(tokens: list, model_name: str):
    encoding = tiktoken.encoding_for_model(model_name)
    text = encoding.decode(tokens)
    return text


def split_in_chunks(all_tokens, max_tokens_in_chunk, sliding_window):
    chunks = list()
    if sliding_window < 0 or sliding_window >= max_tokens_in_chunk:
        return chunks

    num_all_tokens = len(all_tokens)
    if num_all_tokens <= max_tokens_in_chunk:
        chunks.append(list(all_tokens))
        return chunks

    start = 0
    end = max_tokens_in_chunk
    while end < num_all_tokens:
        chunk = all_tokens[start:end]
        chunks.append(chunk)
        start = end - sliding_window
        end = start + max_tokens_in_chunk

    final_chunk = all_tokens[start:num_all_tokens]
    chunks.append(final_chunk)
    return chunks


def create_chunks(entry: dict, chunk_key='html'):
    title = entry.get('title')
    topics = entry.get('topics')
    headings = entry.get('headings')
    url = entry.get('url')
    text = entry.get(chunk_key)
    tokens = encode(text, __model_name)
    chunks = split_in_chunks(tokens, __max_tokens_per_chunk, __sliding_window)
    result = []
    for index, chunk in enumerate(chunks):
        text = decode(chunk, __model_name)
        result.append({
            'title': title,
            'topics': topics,
            'headings': headings,
            'text': text,
            'index': index,
            'url': url
        })
    return result


def process_content(content_path: str, output_path: str):
    result = []
    with open(content_path, 'r') as f:
        content = json.load(f)

    for entry in tqdm.tqdm(content):
        chunks = create_chunks(entry)
        result.extend(chunks)

    print(f'Generated a {len(result)} chunks')
    with open(output_path, 'w') as f:
        json.dump(result, f, indent=2)

if __name__ == '__main__':
    process_content(__content_file, __output_file)