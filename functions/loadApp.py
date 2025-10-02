# load_app.py
import os
import platform
import subprocess
import webbrowser
import shlex

def load_app_mapping(filename="apps.txt"):
    app_mapping = {}
    try:
        with open(filename, 'r') as file:
            for line in file:
                line = line.strip()
                if line and not line.startswith('#'):
                    parts = line.split(':', 2)  # au max 3 morceaux

                    # Cas bundle
                    if parts[0].lower() == "bundle" and len(parts) == 3:
                        bundle_name = parts[1].strip().lower()
                        apps = [app.strip().lower() for app in parts[2].split(',')]
                        app_mapping[f"bundle:{bundle_name}"] = apps

                    # Cas appli simple (chrome: chrome ou spotify: C:\...)
                    elif len(parts) >= 2:
                        key = parts[0].strip().lower()
                        value = parts[1].strip() if len(parts) == 2 else parts[1] + ":" + parts[2]
                        app_mapping[key] = value.strip()

                    else:
                        print(f"Ligne ignorée (format incorrect) : {line}")

    except FileNotFoundError:
        print(f"Erreur : Le fichier de mapping {filename} n'a pas été trouvé.")
    except Exception as e:
        print(f"Erreur lors de la lecture du fichier de mapping : {e}")
    return app_mapping


def open_app(app_entry: str):
    """
    Ouvre une application, une URL ou un chemin, compatible Windows/macOS/Linux.
    - app_entry peut être juste un nom (ex: 'chrome')
    - un chemin complet (ex: 'C:\\...\\Spotify.exe')
    - un chemin avec arguments (ex: 'Update.exe --processStart Discord.exe')
    - ou une URL (ex: 'https://www.youtube.com')
    """
    try:
        system = platform.system()

        # 1. Si c'est une URL
        if app_entry.startswith("http://") or app_entry.startswith("https://"):
            webbrowser.open(app_entry)
            print(f"Ouverture de l'URL : {app_entry}")
            return

        # 2. Windows
        if system == "Windows":
            # Si c’est un chemin complet qui existe
            exe = app_entry.split()[0].strip('"')
            if os.path.exists(exe):
                parts = shlex.split(app_entry)  # découpe correctement les arguments
                subprocess.Popen(parts, shell=False)
                print(f"🚀 Ouverture de {app_entry}")
            else:
                # Sinon on tente via PATH (chrome, notepad, etc.)
                subprocess.Popen(["start", "", app_entry], shell=True)
                print(f"🚀 Ouverture via PATH : {app_entry}")

        # 3. macOS
        elif system == "Darwin":
            subprocess.Popen(["open", app_entry])

        # 4. Linux
        else:
            subprocess.Popen(["xdg-open", app_entry])


    except Exception as e:
        print(f"❌ Je n'ai pas pu ouvrir {app_entry}. Erreur : {e}")