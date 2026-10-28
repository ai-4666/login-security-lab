import subprocess,sys,urllib.request,urllib.parse,json,time
p=subprocess.Popen([sys.executable,"lab.py"],stdout=subprocess.PIPE)
try:
 time.sleep(0.5)
 base="http://127.0.0.1:8765"
 assert b"<!doctype html>" in urllib.request.urlopen(base).read()
 results={}
 for m in ("vulnerable","secure"):
  data=urllib.parse.urlencode({"username":"student' -- ","password":"wrong"}).encode()
  results[m]=json.load(urllib.request.urlopen(urllib.request.Request(base+"/login/"+m,data=data)))
 assert results["vulnerable"]["success"] and not results["secure"]["success"]
 print("HTTP PASS",results)
finally:
 p.terminate()
 p.wait()
