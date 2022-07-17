from DealabsMonitor import DealabsMonitor
from threading import Thread
from time import sleep

monitors = []
threads = []

monitors.append(DealabsMonitor("high-tech", "your webhook", 30))
monitors.append(DealabsMonitor("erreur-de-prix", "your webhook", 30))

def main():
    for monitor in monitors:
        t = Thread(target=monitor.monitor, args=())
        t.start()
        sleep(2)
        threads.append(t)
    for thread in threads:
        thread.join()
    threads.clear()

if __name__ == "__main__":
    main()
