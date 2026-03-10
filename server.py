#!/usr/bin/env python3
import http.server, socketserver, json, subprocess, threading, os, re, time, queue, signal

_q = queue.Queue()
_state = {"running": False, "done": False, "success": False}

def _cmd(c):
    try:
        r = subprocess.run(c, shell=True, capture_output=True, text=True)
        return r.stdout.strip()
    except:
        return ""

def do_scan():
    home = os.path.expanduser("~")
    findings = []
    procs = _cmd("ps aux | grep -iE 'openclaw|clawdbot|clawhub|openclaw-gateway|openclaw-pairing|openclaw-manager' | grep -v grep | grep -v server.py")
    if procs:
        names = sorted({os.path.basename(l.split()[10]) for l in procs.splitlines() if len(l.split()) > 10})
        findings.append({"id":"process","icon":"⚠️","label":"运行中进程","detail":", ".join(names)})
    if _cmd("lsof -i :18789 -sTCP:LISTEN 2>/dev/null | grep -v COMMAND"):
        findings.append({"id":"port","icon":"🔓","label":"开放端口 18789","detail":"Gateway API 对外暴露"})
    if _cmd("launchctl list 2>/dev/null | grep 'ai.openclaw'"):
        findings.append({"id":"launchagent","icon":"🚀","label":"开机自启服务","detail":"ai.openclaw.gateway"})
    if os.path.exists(f"{home}/.openclaw/openclaw.json"):
        findings.append({"id":"credentials","icon":"🔑","label":"Token / 凭证文件","detail":"~/.openclaw/openclaw.json"})
    for pkg in ["openclaw","clawdbot","clawhub"]:
        if os.path.exists(f"/opt/homebrew/lib/node_modules/{pkg}"):
            findings.append({"id":"npm","icon":"📦","label":"npm 全局包","detail":"openclaw, clawdbot, clawhub"})
            break
    zshrc = f"{home}/.zshrc"
    if os.path.exists(zshrc) and re.search(r'openclaw|clawdbot|clawhub', open(zshrc).read(), re.I):
        findings.append({"id":"shell","icon":"💉","label":"Shell 配置注入","detail":"~/.zshrc 含 openclaw 代码"})
    return findings

def _step(label, fn):
    _q.put({"t":"step","label":label,"status":"running"})
    try: fn(); _q.put({"t":"step","label":label,"status":"done"})
    except Exception as e: _q.put({"t":"step","label":label,"status":"error","err":str(e)})

def _kill():
    for p in ["openclaw-gateway","openclaw-pairing","openclaw-manager","openclaw","clawdbot","clawhub"]:
        _cmd(f"pkill -TERM -f '{p}' 2>/dev/null")
    time.sleep(1.5)
    for p in ["openclaw-gateway","openclaw-pairing","openclaw-manager","openclaw","clawdbot","clawhub"]:
        _cmd(f"pkill -KILL -f '{p}' 2>/dev/null")

def _launchagent():
    home = os.path.expanduser("~")
    pl = f"{home}/Library/LaunchAgents/ai.openclaw.gateway.plist"
    _cmd(f"launchctl unload '{pl}' 2>/dev/null")
    _cmd("launchctl remove ai.openclaw.gateway 2>/dev/null")
    if os.path.exists(pl): os.remove(pl)

def _npm():
    for pkg in ["openclaw","clawdbot","clawhub"]:
        _cmd(f"npm uninstall -g '{pkg}' 2>/dev/null")

def _bins():
    home = os.path.expanduser("~")
    for d in ["/opt/homebrew/bin","/usr/local/bin",f"{home}/.local/bin",f"{home}/.npm-global/bin"]:
        for b in ["openclaw","clawdbot","clawhub","clawdhub","openclaw-gateway"]:
            p = f"{d}/{b}"
            if os.path.exists(p) or os.path.islink(p):
                try: os.remove(p)
                except: pass

def _data():
    home = os.path.expanduser("~")
    for p in [f"{home}/.clawdbot",f"{home}/.openclaw",f"{home}/openclaw-manager",
              f"{home}/Library/Application Support/openclaw-manager",
              f"{home}/Library/Caches/com.r00t.openclaw-manager",
              f"{home}/Library/Caches/openclaw-manager",
              f"{home}/Library/Preferences/com.r00t.openclaw-manager",
              f"{home}/Library/Preferences/openclaw-manager",
              f"{home}/Library/Preferences/com.r00t.openclaw-manager.plist",
              f"{home}/Library/Preferences/openclaw-manager.plist"]:
        if os.path.islink(p): os.remove(p)
        elif os.path.isdir(p): _cmd(f"rm -rf '{p}'")
        elif os.path.isfile(p): os.remove(p)

def _shell():
    home = os.path.expanduser("~")
    zshrc = f"{home}/.zshrc"
    if not os.path.exists(zshrc): return
    content = open(zshrc).read()
    if not re.search(r'openclaw|clawdbot|clawhub', content, re.I): return
    open(f"{zshrc}.bak.{int(time.time())}","w").write(content)
    cleaned = "\n".join(l for l in content.splitlines() if not re.search(r'openclaw|clawdbot|clawhub',l,re.I))
    open(zshrc,"w").write(cleaned)

def do_uninstall():
    _state["running"] = True
    for label, fn in [("终止所有进程",_kill),("移除开机自启服务",_launchagent),
                      ("卸载 npm 包",_npm),("删除二进制文件",_bins),
                      ("清除数据和凭证",_data),("清理 Shell 配置",_shell)]:
        _step(label, fn); time.sleep(0.3)
    time.sleep(0.8)
    home = os.path.expanduser("~")
    results = [
        {"label":"端口 18789 已关闭","ok": not bool(_cmd("lsof -i :18789 -sTCP:LISTEN 2>/dev/null | grep LISTEN"))},
        {"label":"开机自启已移除","ok": not bool(_cmd("launchctl list 2>/dev/null | grep ai.openclaw"))},
        {"label":"数据和凭证已清除","ok": not os.path.exists(f"{home}/.openclaw")},
        {"label":"所有进程已终止","ok": not bool(_cmd("ps aux | grep -iE 'openclaw|clawdbot|clawhub' | grep -v grep | grep -v server.py"))},
    ]
    _state["done"] = True; _state["success"] = all(r["ok"] for r in results)
    _q.put({"t":"complete","results":results,"success":_state["success"]})

HTML_PATH = os.path.join(os.path.dirname(__file__), "index.html")

class H(http.server.BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def do_GET(self):
        path = self.path.split("?")[0]
        if path == "/":
            body = open(HTML_PATH, encoding="utf-8").read().encode()
            self._send(200, "text/html; charset=utf-8", body)
        elif path == "/scan":
            self._send(200, "application/json", json.dumps(do_scan()).encode())
        elif path == "/uninstall":
            if not _state["running"]:
                threading.Thread(target=do_uninstall, daemon=True).start()
            self.send_response(200)
            self.send_header("Content-Type","text/event-stream")
            self.send_header("Cache-Control","no-cache")
            self.end_headers()
            while not _state["done"]:
                try:
                    msg = _q.get(timeout=0.4)
                    self.wfile.write(f"data: {json.dumps(msg)}\n\n".encode()); self.wfile.flush()
                    if msg.get("t") == "complete": break
                except queue.Empty:
                    try: self.wfile.write(b": ping\n\n"); self.wfile.flush()
                    except: break
        elif path == "/quit":
            self._send(200, "text/plain", b"bye")
            threading.Thread(target=lambda:(time.sleep(0.3),os.kill(os.getpid(),signal.SIGTERM)),daemon=True).start()
        else:
            self._send(404, "text/plain", b"404")
    def _send(self, code, ct, body):
        self.send_response(code); self.send_header("Content-Type",ct)
        self.send_header("Content-Length",str(len(body))); self.end_headers(); self.wfile.write(body)

def main():
    with socketserver.TCPServer(("127.0.0.1", 0), H) as srv:
        port = srv.server_address[1]
        url = f"http://127.0.0.1:{port}"
        def launch():
            time.sleep(0.5)
            chrome = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
            if os.path.exists(chrome):
                subprocess.Popen([chrome, f"--app={url}", "--window-size=820,680",
                    "--window-position=200,100","--disable-extensions","--no-first-run"])
            else:
                subprocess.Popen(["open", url])
        threading.Thread(target=launch, daemon=True).start()
        try: srv.serve_forever()
        except KeyboardInterrupt: pass

if __name__ == "__main__":
    main()
