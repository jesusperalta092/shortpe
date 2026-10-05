
import subprocess, sys, time, os
ROOT = r"C:\Users\USER\Downloads\Proyecto_Netflix_Dramas"
os.chdir(ROOT)
for i in range(1, 25):
    sys.stderr.write(f"=== LOTE {i} ===\n")
    r = subprocess.run([sys.executable, "build_catalog.py", "60"], cwd=ROOT, capture_output=False)
    if r.returncode != 0:
        sys.stderr.write(f"lote {i} fallo con {r.returncode}\n")
    time.sleep(2)
sys.stderr.write("TODOS LOS LOTES COMPLETADOS\n")
