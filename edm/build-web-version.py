"""Build edm/web/index.html (the "view in browser" page) from the email source.

Run after editing green-interiors-edm.html:  python3 edm/build-web-version.py
"""
import re, pathlib

root = pathlib.Path(__file__).parent
src = (root / "green-interiors-edm.html").read_text()
RAW = "https://raw.githubusercontent.com/bbseverest-cloud/Green/claude/friendly-hypatia-tyb65z/"

head = re.search(r"<head>(.*?)</head>", src, re.S).group(1)
body = re.search(r"<body[^>]*>(.*?)</body>", src, re.S).group(1)

# keep only title, font link and styles from the head
keep = "\n".join(re.findall(r"<title>.*?</title>|<link [^>]*>|<style>.*?</style>", head, re.S))
keep = re.sub(r"<title>.*?</title>", "<title>IGBC Green Interiors</title>", keep)

# the page is the browser version, so drop the preheader and the "open in browser" row
body = re.sub(r"<!-- Preheader.*?</div>\s*", "", body, flags=re.S)
body = re.sub(r"<!-- View online -->.*?</table>\s*", "", body, flags=re.S)
# images ship next to the page; poster downloads stay on GitHub
body = body.replace(RAW + "edm/images/", "images/")
# wider side gutter on phones
body = body.replace('padding:16px 8px 32px;', 'padding:16px 16px 32px;')

out = root / "web" / "index.html"
out.parent.mkdir(exist_ok=True)
out.write_text(keep + "\n" + body.strip() + "\n")
print("wrote", out)
