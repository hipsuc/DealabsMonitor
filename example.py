from DealabsMonitor import DealabsMonitor
from threading import Thread
from time import sleep

monitors = []
threads = []

monitors.append(DealabsMonitor("high-tech", "https://ptb.discord.com/api/webhooks/909822966748020786/sxNOHmPD1ZmjKtDdUp6dpS8r6Wt-mlMncnQj946prdQ34_W_qbx622rWI70TVL8ce8AF", 30))
monitors.append(DealabsMonitor("erreur-de-prix", "https://ptb.discord.com/api/webhooks/909822966748020786/sxNOHmPD1ZmjKtDdUp6dpS8r6Wt-mlMncnQj946prdQ34_W_qbx622rWI70TVL8ce8AF", 30))

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