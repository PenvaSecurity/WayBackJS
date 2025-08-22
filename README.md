# WayBackJS
A simple python script for scraping historical JavaScript files from the Wayback Machine to assist in passive reconnaissance during web application penetration testing.
<img src="https://i.postimg.cc/2SKyMcbM/waybackjs.png">

---

### About
- WaybackJS scrapes archived .js files of a target domain from the Wayback Machine (Internet Archive).
- It is designed to aid in security testing by revealing potentially sensitive or deprecated client-side code, internal API references, or forgotten secrets in legacy JavaScript files.

---

### Setting up
```
git clone https://github.com/PenvaSecurity/WayBackJS
cd WayBackJS
python3 waybackjs.py -h
```

---

### Features
- Filters only valid .js files from the files fetched from Wayback archive.
- Strips archive prefixes/postfixes injected by the Wayback Machine.
- Removes duplicate files (using SHA256 hashing).

---

### How to Use
Run the tool from terminal with your target domain:
```
python3 waybackjs.py example.com
```
You can specify a custom date range using --initialdate and --enddate (format: YYYYMMDD):
```
python3 waybackjs.py example.com --initialdate 20100101 --enddate 20250101
```

---

### Output Structure
```
WaybackJS/
├── waybackjs.py
├── active_js_files.output         # URLs of JS files that were successfully downloaded
├── downloaded_js_files/           # Cleaned and deduplicated JS files
│   ├── _20200101_https___example_com_script_js
│   └── ...
```
