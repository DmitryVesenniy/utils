import sys
import time
import subprocess
from getpass import getpass
# types
from typing import List


class StatusDrive:
    def __init__(self, pswd: str) -> None:
        self.pswd = pswd
    
    def is_package(self, packages: str="smartmontools") -> bool:
        p = subprocess.Popen("dpkg -s %s" % packages, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE, shell=True)
        res = self.await_shell(p)
        
        if res != 0:
            print("Программа завершилась с ошибкой: ")
            print(p.stderr.read().decode("utf8"))
            sys.exit(1)
            
        try:
            resp = p.stdout.read().decode()

        except Exception as e:
            print("Во время работы программы возникла ошибка: %s" % e)
            return False

        if 'Status: install ok installed' in resp:
            return True

        return False
    
    def install_package(self, packages: str) -> (int, str):
        p = subprocess.Popen("echo '%s' | sudo -S apt-get install -y --allow-unauthenticated %s" %\
            (self.pswd, packages), stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        return self.await_shell(p), p.stderr.read().decode("utf8")
        
    def await_shell(self, process: subprocess.Popen) -> int:
        while process.poll() is None:
            time.sleep(1)
        return process.poll()
    
    def get_list_devices(self) -> List[str]:
        p = subprocess.Popen("smartctl --scan", stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             shell=True)
                
        if self.await_shell(p) != 0:
            print("Не удалось получить список дисков!!")
            print(p.stderr.read().decode("utf8"))
            sys.exit(1)
        
        res = p.stdout.read().decode("utf8")

        return list(map(lambda x: x.split()[0], filter(lambda x: bool(x) and len(x.split()) > 0, res.split("\n"))))
    
    def info_device(self, device: str) -> subprocess.Popen:
        p = subprocess.Popen("echo '%s' | sudo -S smartctl -i %s" %
            (self.pswd, device), stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        
        self.await_shell(p)
        return p
    
    def get_state_device(self, device: str) -> subprocess.Popen:
        p = subprocess.Popen("echo '%s' | sudo -S smartctl -A %s" %
            (self.pswd, device), stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    
        self.await_shell(p)
        return p

    def is_passed(self, device: str) -> subprocess.Popen:
        p = subprocess.Popen("echo '%s' | sudo -S smartctl -H %s" %
            (self.pswd, device), stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    
        self.await_shell(p)
        return p
    
    def __call__(self):
        smart = self.is_package("smartmontools")
        if not smart:
            install_result, err = self.install_package("smartmontools")
            if install_result != 0:
                print("Не удалось установить пакет <smartmontools>, Err: %s" % err)
                sys.exit(1)
                
        print("Получение списка дисков...")
        devices = self.get_list_devices()
        print(devices)
        
        for device in devices:
            info_await_process: subprocess.Popen = self.info_device(device)
            if info_await_process.poll() != 0:
                print("Не удалось получить информацию о диске!!")
                print(info_await_process.stderr.read().decode("utf8"))
                
            else:
                print("*" * 80)
                print(info_await_process.stdout.read().decode("utf8"))
                
            state_await_process: subprocess.Popen = self.get_state_device(device)
            if state_await_process.poll() != 0:
                print("Не удалось получить информацию о состоянии диска!!")
                print(state_await_process.stderr.read().decode("utf8"))
                
            else:
                print(state_await_process.stdout.read().decode("utf8"))

            passed_await_process: subprocess.Popen = self.is_passed(device)
            if passed_await_process.poll() != 0:
                print("Не удалось получить информацию о состоянии диска!!")
                print(passed_await_process.stderr.read().decode("utf8"))
                
            else:
                print(passed_await_process.stdout.read().decode("utf8"))
                
                
def main():
    pswd = getpass('Password:')
    status = StatusDrive(pswd)
    status()
    
    
if __name__ == "__main__":
    main()
