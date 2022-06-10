import subprocess
import threading
import time
import queue
import os


def output_reader(proc, outq):
    for line in iter(proc.stdout.readline, b''):
        outq.put(line.decode('utf-8'))

def start_server():
    proc = subprocess.Popen(['python3', '-u', 'tcp_server.py'],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT)

    outq = queue.Queue()

    t = threading.Thread(target=output_reader, args=(proc, outq))
    t.start()

    try:
        time.sleep(0.2)
        for i in range(4):
            time.sleep(0.1)
            try:
                line = outq.get(block=False)
                print(line, end='')
            except queue.Empty:
                print('could not get line from queue')
    finally:
        stop_server(proc)
    t.join()

def stop_server(proc):
    proc.terminate()
    try:
        proc.wait(timeout=0.2)
        print('== subprocess exited with rc =', proc.returncode)
    except subprocess.TimeoutExpired:
        print('subprocess did not terminate in time')
        proc.kill()

def main():
    start_server()


if __name__ == "__main__":
    main()