import requests, re, os, hashlib, shutil, time, argparse
from pathlib import Path

def hash_file(filepath, algo='sha256', chunk_size=4096):
    h = hashlib.new(algo)
    with open(filepath, 'rb') as f:
        while chunk := f.read(chunk_size):
            h.update(chunk)
    return h.hexdigest()

def remove_duplicates(directory):
    seen_hashes = {}
    deleted_files = []
    for root, dirs, files in os.walk(directory):
        for filename in files:
            filepath = os.path.join(root, filename)
            try:
                file_hash = hash_file(filepath)
                if file_hash in seen_hashes:
                    # Duplicate found, remove file
                    os.remove(filepath)
                    deleted_files.append(filepath)
                    print(f"Removed duplicate: {filepath}")
                else:
                    seen_hashes[file_hash] = filepath
            except Exception as e:
                print(f"Could not process {filepath}: {e}")
    print(f"\nFinished. Total duplicates removed: {len(deleted_files)}")

def extract_middle_js_content(js_code):
    prefix_pattern = re.compile(r'^.*?let opener = .*?;\s*', re.DOTALL)
    postfix_pattern = re.compile(r'\}\s*/\*\s*FILE ARCHIVED ON.*$', re.DOTALL)
    js_without_prefix = prefix_pattern.sub('', js_code)
    js_middle_content = postfix_pattern.sub('', js_without_prefix)
    return js_middle_content.strip()


try:
    os.remove('active_js_files.output')
except FileNotFoundError:
    pass
if os.path.exists('downloaded_js_files'):
    shutil.rmtree('downloaded_js_files')

print(r"""
__        __          ____             _       _ ____  
\ \      / /_ _ _   _| __ )  __ _  ___| | __  | / ___| 
 \ \ /\ / / _` | | | |  _ \ / _` |/ __| |/ /  | \___ \ 
  \ V  V / (_| | |_| | |_) | (_| | (__|   < |_| |___) |
   \_/\_/ \__,_|\__, |____/ \__,_|\___|_|\_\___/|____/ 
                |___/                                  
                                                      developed by PenvaSecurity
""")

parser = argparse.ArgumentParser(
        description="Scrap JS files using wayback machine.", add_help=True
)

parser.add_argument(
        "domain",
        help="The name of the domain"
)

parser.add_argument(
        "--initialdate",
        type=str,
        default="19950101",
        help="Set initial date (default: 19950101)"
)

parser.add_argument(
        "--enddate",
        type=str,
        default="20250707",
        help="Set end date (default: 20250707)"
)

args = parser.parse_args()

condition = False
while(condition==False):
    try:
        res = requests.get("https://web.archive.org/cdx/search/cdx?url=*." + args.domain + "/*&from=" + args.initialdate + "&to=" + args.enddate + "&output=json&fl=timestamp,original", timeout=60)
        condition = True
    except Exception as e:
        pass
json_res = res.json()
result = {row[0]: row[1] for row in json_res[1:]}

matched_dict = {k: v for k, v in result.items() if re.search(r'\.js([?#]|$)', v)}
print("Length of original result: "+str(len(json_res)))
print("Length of result with .js files: "+str(len(matched_dict)))


file_path = 'active_js_files.output'
with open(file_path, 'w') as f:
    for key, value in matched_dict.items():
        condition = False
        while condition == False:
            try:
                #print("IN TRY")
                url = "https://web.archive.org/web/" + key + "if_/" + value
                #time.sleep(1)
                response = requests.get(url, timeout=30)
                if response.status_code == 200:
                    print("[200]: " + url)
                    f.write(url + '\n')
                    condition = True
                else:
                    condition = True
            except Exception as e:
                pass

f.close()

print(f"Values saved to {file_path}")

os.mkdir('downloaded_js_files')
os.chdir('downloaded_js_files')
print("Starting Downloading JS Files...")
with open('../active_js_files.output', 'r') as f:
    count = 0
    for url in f.readlines():
        filename = url[url.find("https://web.archive.org/web/")+len("https://web.archive.org/web/"):].replace('if_/https://','_').replace('/','_')[:-1]
        with open(filename, 'w') as f2:
            condition = False
            while(condition==False):
                try:
                    response = requests.get(url[:-1], timeout=30)
                    f2.write(response.text)
                    print("Downloaded: "+filename)
                    count += 1
                    condition = True
                except Exception as e:
                    pass
f.close()


print("Total files downloaded: " + str(count))

print("Removing prefix and postfix from all files...")
current_dir = Path('.')
js_files = list(current_dir.iterdir())
for js_file in js_files:
    try:
        content = js_file.read_text(encoding='utf-8')
        cleaned_content = extract_middle_js_content(content)
        js_file.write_text(cleaned_content, encoding='utf-8')
        print(f"Cleaned: {js_file.name}")
    except Exception as e:
        print(f"Error processing {js_file.name}: {e}")


print("Finding and removing duplicated files now...")
remove_duplicates(os.getcwd())
