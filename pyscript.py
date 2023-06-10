import subprocess
#subprocess.call('start /wait python3 AttributeCertifier.py --title "Identity Certificate" --name IdP --req-ip 127.0.0.1 --req-port 3001 --open-ip 127.0.0.1 --open-port 7001', shell=True)

#subprocess.call(['gnome-terminal', '-x', 'python3 /media/user/New Volume/IITH/Thesis/Pavan DTRAC/ModifierVersionGanache-20220827T104628Z-001/ModifierVersionGanache/AttributeCertifier.py --title "Identity Certificate" --name IdP --req-ip 127.0.0.1 --req-port 3001 --open-ip 127.0.0.1 --open-port 7001'])

#subprocess.call_in_new_window('python3 AttributeCertifier.py --title "Identity Certificate" --name IdP --req-ip 127.0.0.1 --req-port 3001 --open-ip 127.0.0.1 --open-port 7001', shell=True)

subprocess.call(['gnome-terminal', '-x', '/home/neel/acad/DTRAC/ravc-main/hello.py'])
