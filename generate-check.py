try:
    import sys
    import os
    import time
    import requests
    import re
    import regex
    import math
    import concurrent.futures
    import itertools
except ImportError:
    print("Trying to install the required modules! THIS MAY DISPLAY LARGE ERRORS!\nPlease try to run this script again once all of the modules have been successfully installed.\n\n")
    input("press enter to start installing... ")
    os.system("py -m pip install -r requirements.txt")
    os.system("python -m pip install -r requirements.txt")
    os.system("python3 -m pip install -r requirements.txt")
    input("\n\ndone installing modules! please restart the script now. Press enter to continue... ")
    sys.exit()

def check_username(username):
    retry = True
    while retry:
        retry = False
        # result = bool(regex.search(username))
        result = False
        if not (result or (len(username) < 3) or (len(username) > 16)):
            res = requests.get('https://api.mojang.com/users/profiles/minecraft/' + username)

            if res.status_code == 200:
                print(f'{username} is taken. ☓')
                unavailable_names.append(username)

            elif res.status_code == 204:
                print(f'{username} is available or never used. ✓')
                # from stackoverflow:
                # concurrent.futures.ThreadPoolExecutor allow only one thread to access the common data structure or location in memory at a time; the threading.Lock() primitive is used to manage this, so race conditions don't occur!
                available_names.append(username)

            elif res.status_code == 429:
                end_time = time.time()
                global start_time
                time_to_wait = math.ceil(600 - (end_time - start_time))
                global rate_limited
                if not rate_limited:
                    rate_limited = True
                    print(f'Request is being refused due to IP being rate limited. Waiting {time_to_wait} seconds before reattempting...')
                    names_checked = len(available_names)+len(unavailable_names)+len(invalid_names)
                    print(f'Progress so far:\nUsernames checked: {names_checked}\nTotal usernames: {len(names_to_check)}\nUsernames left to go: {len(names_to_check)-names_checked}')
                    print(f'Available usernames (so far): {len(available_names)}\nUnavailable usernames (so far): {len(unavailable_names)}\nInvalid usernames (so far): {len(invalid_names)}')
                retry = True
                time.sleep(time_to_wait)
                rate_limited = False
                start_time = time.time()

            else:
                res.raise_for_status()
                print(f'Unhandled HTTP status code: {res.status_code}. Exiting...')
                sys.exit()
        else:
            print(f'{username} is an invalid username. ϟ')
            invalid_names.append(username)

if __name__ == "__main__":
    print("This mode will generate names.")

    username = "!!!!"
    invalid_names = []
    available_names = []
    unavailable_names = []
    names_to_check = []

    start_time = time.time()
    rate_limited = False

    all_chars = {'_','0','1','2','3','4','5','6','7','8','9','a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z'}
    letters_only = {'a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z'}
    numbers_only = {'0','1','2','3','4','5','6','7','8','9'}

    good_chars = letters_only
    name_length = 4

    def l_to_d(lst):
        res_dct = {lst[i]: lst[i + 1] for i in range(0, len(lst), 2)}
        return res_dct

    def chooseMode():
        global good_chars, letters_only, numbers_only, all_chars
        mode = input("Please choose: only letters (letters), only numbers (numbers), all characters (all), or custom (custom): ").lower()
        if mode in ['letters','l','let']:
            good_chars = letters_only
        elif mode in ['numbers','n','num']:
            good_chars = numbers_only
        elif mode in ['all','a']:
            good_chars = all_chars
        elif mode in ['custom', 'c', 'cust']:
            custom_chars = []
            done = False
            while not done:

                newChar = input('Type a character or "done": ').lower()
                if newChar in all_chars:

                    if newChar not in custom_chars:
                        custom_chars.append(newChar)
                        print(f'"{newChar}" added to custom list.')
                        print(f'Custom List: {custom_chars}')
                    else:
                        None

                elif newChar == "done":
                    print(f"List finalized. Custom List: {custom_chars}")
                    done = True

                else:
                    print("Invalid character. Allowed characters include a-z, 0-9, and _")

            #good_chars = {}
            #for i in custom_chars:
            #    good_chars.append(i)

            good_chars = ''.join(custom_chars)

        else:
            print("Invalid choice. Please try again.")
            chooseMode()

    def chooseLength():
        global length_choice, name_length
        length_choice = input("Please enter the desired length you want to generate. Must be an integer 3-16.: ")
        try:
            name_length = int(length_choice)
        except:
            print("Input must be an integer from 3 to 16!")
            chooseLength()
        else:
            if 2 < int(length_choice) < 17:
                name_length = int(length_choice)
            else:
                print("Input must be from 3 to 16.")
                chooseLength()

    chooseMode()
    chooseLength()
    print("\n\nLoading all possible names...")

    # override
    # good_chars = letters_only
    # name_length = 4

    time_split = str(time.time()).split('.')
    process_start_time = int(time_split[0])

    for i in itertools.product(good_chars, repeat=name_length):
        names_to_check.append(''.join(i))

    # print all possible names to check
    print("\n-------------------------\nNAMES TO CHECK:\n")
    for i in names_to_check:
        print(i)
    print("\n-------------------------\n")

    # NOT multithreading
    # for i in names_to_check:
    #    check_username(i)

    # check names
    # use of multithreading
    print(f"Checking {len(names_to_check)} names...\n")

    with concurrent.futures.ThreadPoolExecutor() as executor:
        try:
            executor.map(check_username, names_to_check)
        except Exception as exc:
            print(f'There is a problem: {exc}. Exiting...')
            sys.exit()

    # print results
    print("\nProcess complete.")

    print(f"\n-------------------------\n{len(invalid_names)} INVALID NAMES:   ϟ\n")
    if len(invalid_names) > 0:
        for i in invalid_names:
            print("ϟ "+i)
    else:
        print("None Found")
    print("\n-------------------------\n\n")

    print(f"\n-------------------------\n{len(unavailable_names)} UNAVAILABLE NAMES:   ☓\n")
    if len(unavailable_names) > 0:
        for i in unavailable_names:
            print("☓ "+i)
    else:
        print("None Found")
    print("\n-------------------------\n\n")

    print(f"\n-------------------------\n{len(available_names)} AVAILABLE NAMES:   ✓\n")
    if len(available_names) > 0:
        for i in available_names:
            print("✓ "+i)
    else:
        print("None Found")
    print("\n-------------------------\n")

    # find time taken
    time_split = str(time.time()).split('.')
    process_end_time = int(time_split[0])

    time_taken = process_end_time - process_start_time
    time_taken = str(time_taken)

    # print final message
    print(f"\n\nDone! That took {time_taken} seconds and found {len(available_names)} available names.\nPlease Note: Some names may be blocked by Mojang for any reason, and this was not detected by the script.\n")
