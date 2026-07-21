"""baixa_export_drive.py — Pipeline #28 (coleta censitária)

Baixa os shards exportados por `export_cubo_mapbiomas_go.py` do Google Drive
para `data/raw/cubo_go/`.

Reaproveita as credenciais gravadas por `earthengine authenticate`: elas já
carregam o escopo `auth/drive` (além de `earthengine`, `cloud-platform` e
`devstorage`), então não é preciso montar um fluxo OAuth separado. O
`refresh_token` fica em ~/.config/earthengine/credentials e nunca é impresso.

Como rodar:
    python scripts/baixa_export_drive.py                 (baixa o que faltar)
    python scripts/baixa_export_drive.py --listar        (só lista, não baixa)
    python scripts/baixa_export_drive.py --prefixo cubo_go_TESTE
"""
from __future__ import annotations

import argparse
import io
import json
import os
import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

from ee import oauth
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

ROOT = Path(__file__).resolve().parent.parent
DIR_SAIDA = ROOT / "data" / "raw" / "cubo_go"
CRED = Path(os.path.expanduser("~/.config/earthengine/credentials"))
TOKEN_URI = "https://oauth2.googleapis.com/token"


def servico_drive():
    if not CRED.exists():
        sys.exit(f"Credenciais não encontradas em {CRED}\nRode: earthengine authenticate")
    d = json.loads(CRED.read_text())
    if "drive" not in " ".join(d.get("scopes", [])):
        sys.exit("As credenciais do GEE não têm escopo Drive. Reautentique com "
                 "`earthengine authenticate --scopes drive`.")
    creds = Credentials(
        token=None,
        refresh_token=d["refresh_token"],
        client_id=oauth.CLIENT_ID,
        client_secret=oauth.CLIENT_SECRET,
        token_uri=TOKEN_URI,
        scopes=d.get("scopes"),
    )
    return build("drive", "v3", credentials=creds, cache_discovery=False)


def listar(svc, prefixo: str) -> list[dict]:
    arquivos, token = [], None
    while True:
        r = svc.files().list(
            q=f"name contains '{prefixo}' and trashed = false and "
              f"mimeType != 'application/vnd.google-apps.folder'",
            fields="nextPageToken, files(id, name, size, md5Checksum)",
            pageSize=200,
            pageToken=token,
        ).execute()
        arquivos.extend(r.get("files", []))
        token = r.get("nextPageToken")
        if not token:
            break
    return sorted(arquivos, key=lambda f: f["name"])


def baixar(svc, arq: dict, destino: Path) -> bool:
    """Retorna True se baixou, False se já existia com o tamanho certo."""
    tam = int(arq.get("size", 0))
    if destino.exists() and destino.stat().st_size == tam:
        print(f"  {arq['name']} — já existe ({tam / 1e6:.1f} MB)")
        return False
    destino.parent.mkdir(parents=True, exist_ok=True)
    parcial = destino.with_suffix(destino.suffix + ".parcial")
    with open(parcial, "wb") as fh:
        dl = MediaIoBaseDownload(fh, svc.files().get_media(fileId=arq["id"]),
                                 chunksize=32 * 1024 * 1024)
        feito = False
        while not feito:
            status, feito = dl.next_chunk()
            if status:
                print(f"\r  {arq['name']} — {status.progress() * 100:5.1f}%", end="")
    parcial.replace(destino)
    print(f"\r  {arq['name']} — {destino.stat().st_size / 1e6:.1f} MB  ok    ")
    return True


def main() -> None:
    p = argparse.ArgumentParser(description="Baixa os shards do export do Drive")
    p.add_argument("--prefixo", default="cubo_go")
    p.add_argument("--listar", action="store_true")
    p.add_argument("--saida", type=Path, default=DIR_SAIDA)
    args = p.parse_args()

    svc = servico_drive()
    arquivos = listar(svc, args.prefixo)
    if not arquivos:
        sys.exit(f"Nenhum arquivo com prefixo '{args.prefixo}' no Drive.")

    total = sum(int(a.get("size", 0)) for a in arquivos)
    print(f"{len(arquivos)} arquivo(s) | {total / 1e9:.2f} GB no Drive")
    if args.listar:
        for a in arquivos:
            print(f"  {a['name']:52s} {int(a.get('size', 0)) / 1e6:8.1f} MB")
        return

    baixados = 0
    for a in arquivos:
        if baixar(svc, a, args.saida / a["name"]):
            baixados += 1
    print(f"\n{baixados} baixado(s), {len(arquivos) - baixados} já presente(s)")
    print(f"Destino: {args.saida}")


if __name__ == "__main__":
    main()
