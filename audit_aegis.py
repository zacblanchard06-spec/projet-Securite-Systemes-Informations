import subprocess
import os
from datetime import datetime


PORT_ATTENDU = "2222"
SERVICES = ["ssh", "fail2ban"]
FICHIER_RAPPORT = "rapport_audit.txt"

def run_command(cmd):
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.stdout.strip()
    except Exception as e:
        return f"Erreur: {str(e)}"

def generer_audit():
    print(f"\n=== LANCEMENT DE L'AUDIT SÉCURITÉ AEGIS ===")
    lignes_rapport = [f"AUDIT DU {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", "-"*40]

    for svc in SERVICES:
        status = run_command(f"systemctl is-active {svc}")
        res = f"[OK] Service {svc.upper()} est actif" if status == "active" else f"[!!] Service {svc.upper()} est HS"
        print(res)
        lignes_rapport.append(res)

    netstat = run_command("ss -tulnp | grep sshd")
    if PORT_ATTENDU in netstat:
        res = f"[OK] SSH écoute bien sur le port {PORT_ATTENDU}"
    else:
        res = f"[ALERTE] SSH ne semble pas écouter sur le port {PORT_ATTENDU} !"
    print(res)
    lignes_rapport.append(res)

    config_ssh = run_command("grep '^PasswordAuthentication' /etc/ssh/sshd_config")
    if "no" in config_ssh:
        res = "[OK] Authentification par mot de passe : DÉSACTIVÉE"
    else:
        res = "[DANGER] Authentification par mot de passe : ENCORE ACTIVE"
    print(res)
    lignes_rapport.append(res)

    f2b_stats = run_command("sudo fail2ban-client status sshd")
    if "Status for the jail: sshd" in f2b_stats:
        lignes = f2b_stats.split('\n')
        banned = [l for l in lignes if "Banned IP list" in l]
        res = f"[INFO] Fail2Ban : {banned[0] if banned else 'Aucun banni'}"
    else:
        res = "[ALERTE] Fail2Ban ne surveille pas la jail SSHD"
    print(res)
    lignes_rapport.append(res)


    with open(FICHIER_RAPPORT, "w") as f:
        f.write("\n".join(lignes_rapport))
    print(f"\n--- Audit terminé. Rapport sauvegardé dans {FICHIER_RAPPORT} ---")

if __name__ == "__main__":
    if os.geteuid() != 0:
        print("ERREUR : Ce script doit être lancé avec 'sudo' pour accéder aux logs et services.")
    else:
        generer_audit()
