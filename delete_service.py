#!/usr/bin/env python3
import os
import sys
import shutil
import subprocess
from pathlib import Path
import re

NAMESPACE = "bt-api"


def run(cmd: list[str]) -> int:
    print(f"[INFO] {' '.join(cmd)}")
    return subprocess.run(cmd, check=False).returncode


def docker_compose_stop_rm(service: str) -> None:
    # Dừng và xóa container của service trong docker compose (nếu có khai báo)
    run(["docker", "compose", "stop", service])
    run(["docker", "compose", "rm", "-f", service])


def docker_kill_leftover(service: str) -> None:
    # Thử xóa các container còn sót lại theo pattern tên
    try:
        out = subprocess.check_output(["docker", "ps", "-a", "--format", "{{.ID}} {{.Image}} {{.Names}}"], text=True)
        for line in out.splitlines():
            parts = line.split(" ", 2)
            if len(parts) < 2:
                continue
            cid = parts[0]
            img = parts[1]
            name = parts[2] if len(parts) > 2 else ""
            if service in img or service in name:
                run(["docker", "rm", "-f", cid])
    except Exception:
        pass


def docker_remove_image(service: str) -> None:
    # Xóa image đặt theo convention của repo
    run(["docker", "rmi", f"bt_api-{service}:latest"])
    # Xóa thêm các image có tên chứa service (phòng trường hợp tag khác)
    try:
        out = subprocess.check_output(["docker", "images", "--format", "{{.Repository}}:{{.Tag}} {{.ID}}"], text=True)
        for line in out.splitlines():
            repo_tag, _img_id = (line.split(" ", 1) + [""])[:2]
            if service in repo_tag:
                run(["docker", "rmi", repo_tag])
    except Exception:
        pass


def k8s_delete_resources(service: str) -> None:
    # Xóa Deployment & Service theo label "service=<service>"
    run(["kubectl", "delete", "deployment,svc", "-l", f"service={service}", "-n", NAMESPACE])
    # Xóa file manifest nếu có
    manifest = Path("k8s/manifests") / f"{service}-deployment.yaml"
    if manifest.exists():
        try:
            manifest.unlink()
            print(f"[SUCCESS] Deleted manifest file: {manifest}")
        except Exception as exc:
            print(f"[ERROR] Could not delete manifest file {manifest}: {exc}")
    else:
        print(f"[INFO] Manifest file not found (skip): {manifest}")


def ingress_remove_backend(service: str) -> None:
    ingress_path = Path("k8s/manifests/ingress.yaml")
    if not ingress_path.exists():
        print(f"[INFO] Ingress file not found (skip): {ingress_path}")
        return
    try:
        original = ingress_path.read_text(encoding="utf-8")
    except Exception:
        original = ingress_path.read_text(encoding="utf-8", errors="ignore")

    # Loại bỏ block path trỏ về <service>-service trong ingress (rule theo backend service name)
    pattern = re.compile(
        r"\n\s*-\s*path:.*?\n(?:\s*.*?\n)*?\s*name:\s*"
        + re.escape(f"{service}-service")
        + r"\s*\n(?:\s*.*?\n)*?(?=\n\s*-\s*path:|\Z)",
        re.MULTILINE,
    )
    new_content, num_subs = pattern.subn("\n", original)
    if num_subs > 0:
        backup = ingress_path.with_suffix(".bak")
        try:
            ingress_path.replace(backup)
            ingress_path.write_text(new_content, encoding="utf-8")
            print(f"[SUCCESS] Removed {num_subs} ingress path block(s) for '{service}'. Backup: {backup}")
            print("[INFO] Re-apply ingress if needed: kubectl apply -f k8s/manifests/ingress.yaml")
        except Exception as exc:
            print(f"[ERROR] Failed updating ingress: {exc}")
            try:
                if ingress_path.exists():
                    ingress_path.unlink(missing_ok=True)  # type: ignore[arg-type]
                backup.replace(ingress_path)
            except Exception:
                pass
    else:
        print(f"[INFO] No matching ingress rule found for backend '{service}-service' (skip)")


def delete_service_folder(service: str) -> None:
    svc_dir = Path("services") / service
    if svc_dir.exists():
        try:
            shutil.rmtree(svc_dir)
            print(f"[SUCCESS] Deleted folder: {svc_dir}")
        except Exception as exc:
            print(f"[ERROR] Could not delete folder {svc_dir}: {exc}")
    else:
        print(f"[INFO] Service folder not found (skip): {svc_dir}")


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python delete_service.py <service_name>")
        return 2
    service = sys.argv[1].strip()
    if not service:
        print("[ERROR] service_name is empty")
        return 2

    print(f"[INFO] Deleting service '{service}' from Docker & Kubernetes...")

    # 1) Docker: stop & remove compose containers + leftovers + image
    docker_compose_stop_rm(service)
    docker_kill_leftover(service)
    docker_remove_image(service)

    # 2) Kubernetes: delete deployment & service & manifest, clean ingress
    k8s_delete_resources(service)
    ingress_remove_backend(service)

    # 3) Optional: delete local service folder
    delete_service_folder(service)

    print("[DONE] Completed deletion attempts. Review messages above for any skips/errors.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


