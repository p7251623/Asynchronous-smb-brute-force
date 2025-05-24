# Asynchronous SMB Brute Force

This repository contains an asynchronous Python script for brute forcing SMB (Server Message Block) logins. The script is designed for use in penetration testing environments such as Hack The Box, and allows you to efficiently try username/password combinations with concurrency and retry logic.

## Features

- Asynchronous brute force using Python's `asyncio`
- Concurrency control to avoid socket exhaustion
- Exponential backoff and retry for resource exhaustion errors
- Reads username and password lists from files

## Usage

1. **Install Requirements**

   You need Python 3.8+ and the `impacket` library. Install dependencies with:

   ```bash
   pip install impacket
   ```

2. **Prepare Username and Password Files**

   - Place your username list in `Usernames.txt`
   - Place your password list in `Passwords.txt`
   - Each entry should be on a new line

3. **Configure the Target**

   Edit the `TARGET` variable at the top of `smb_bruteforce.py` to point to the SMB server's IP address.

4. **Run the Script**

   ```bash
   python smb_bruteforce.py
   ```

## Legal Notice

This script is for educational and authorized penetration testing use only! Do not use it on systems you do not have explicit permission to test.

## License

MIT License