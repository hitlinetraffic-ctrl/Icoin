# python full_check.py — полный быстрый чек (dev)
import os
import requests

NODES = [
    ("delegate1", "http://localhost:8001"),
    ("delegate2", "http://localhost:8002"),
]
API_PASSWORD = os.getenv("API_PASSWORD", "change-me")

def get_token(url: str) -> str:
    r = requests.post(f"{url}/auth/token", json={"password": API_PASSWORD}, timeout=10)
    r.raise_for_status()
    return r.json()["token"]

def main():
    print("FULL CHECK ICOIN (dev)")
    ok_all = True
    for name, url in NODES:
        try:
            # health без auth
            h = requests.get(f"{url}/health", timeout=5)
            if h.status_code != 200:
                print(f"{name}: health FAIL {h.status_code}")
                ok_all = False
                continue

            token = get_token(url)
            headers = {"Authorization": f"Bearer {token}"}

            s = requests.get(f"{url}/security", headers=headers, timeout=10)
            c = requests.get(f"{url}/chain", headers=headers, timeout=10)

            print(f"{name}: security={s.status_code} chain={c.status_code} blocks={len(c.json()) if c.status_code==200 else '-'}")
        except Exception as e:
            print(f"{name}: ERROR {e}")
            ok_all = False

    if not ok_all:
        raise SystemExit(1)
    print("OK")

if __name__ == "__main__":
    main()
