import yaml
import imaplib
import logging
import email
from bs4 import BeautifulSoup
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed

NUM_THREADS = 10

def get_credentials(filepath):
    try:
        with open(filepath, 'r') as file:
            credentials = yaml.safe_load(file)
            user = credentials['user']
            password = credentials['password']
            return user, password
    except (yaml.YAMLError, FileNotFoundError) as e:
        logging.error("Failed to load credentials: {}".format(e))
        raise

def connect_to_gmail_imap(user, password):
    imap_url = 'imap.gmail.com'
    try:
        mail = imaplib.IMAP4_SSL(imap_url)
        mail.login(user, password)
        mail.select('inbox')
        return mail
    except imaplib.IMAP4.error as e:
        logging.error("Connection failed: {} Try reducing the number of threads.".format(e))
        raise

def get_all_emails_having_unsubscibe_link(mail):
    try:
        result, data = mail.search(None, '(BODY "unsubscribe")')
        if result == 'OK':
            email_ids = data[0].split()
            return email_ids
        else:
            logging.error("Failed to search emails")
            return []
    except imaplib.IMAP4.error as e:
        logging.error("Failed to retrieve emails: {}".format(e))
        raise

def get_unsubscribe_links(mail, email_id):
    try:
        result, data = mail.fetch(email_id, '(RFC822)')
        if result == 'OK':
            msg = email.message_from_bytes(data[0][1])
            unsubscribe_links = []

            # Check for List-Unsubscribe header
            if 'List-Unsubscribe' in msg:
                list_unsubscribe = msg['List-Unsubscribe']
                unsubscribe_links += [link.strip('<> ') for link in list_unsubscribe.split(',') if 'http' in link]

            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == 'text/html':
                        body = part.get_payload(decode=True)
                        soup = BeautifulSoup(body, 'html.parser')
                        links = soup.find_all('a', href=True)
                        unsubscribe_links += [link['href'] for link in links if 'unsubscribe' in link.text.lower()]
            else:
                if msg.get_content_type() == 'text/html':
                    body = msg.get_payload(decode=True)
                    soup = BeautifulSoup(body, 'html.parser')
                    links = soup.find_all('a', href=True)
                    unsubscribe_links += [link['href'] for link in links if 'unsubscribe' in link.text.lower()]

            from_email = msg['From']
            return unsubscribe_links, from_email
        return [], None
    except Exception as e:
        return [], None

def get_unsubscribe_links_thread(mail, email_ids_split_part, progress_bar, set_of_links):
    for email_id in email_ids_split_part:
        links, from_email = get_unsubscribe_links(mail, email_id)
        if from_email is None:
            continue

        if from_email in set_of_links:
            set_of_links[from_email].update(links)
        else:
            set_of_links[from_email] = set(links)
        progress_bar.update(1)
    return set_of_links

def get_all_emails_having_unsubscibe_link_threaded(mails, email_ids):
    email_ids_split = [email_ids[i::NUM_THREADS] for i in range(NUM_THREADS)]
    set_of_links = [{} for _ in range(NUM_THREADS)]

    with tqdm(total=len(email_ids)) as progress_bar:
        with ThreadPoolExecutor(max_workers=NUM_THREADS) as executor:
            futures = [
                executor.submit(get_unsubscribe_links_thread, mail, email_ids_split_part, progress_bar, return_value)
                for email_ids_split_part, mail, return_value in zip(email_ids_split, mails, set_of_links)
            ]

            for future in as_completed(futures):
                future.result()

    single_set_of_links = {}
    for links in set_of_links:
        for email, link_set in links.items():
            if email in single_set_of_links:
                single_set_of_links[email].update(link_set)
            elif link_set:
                single_set_of_links[email] = link_set
    return single_set_of_links

def main():
    credentials = get_credentials('credentials.yaml')

    print("Connecting to Gmail IMAP...")
    mails = [connect_to_gmail_imap(*credentials) for _ in range(NUM_THREADS)]
    print("Connected to Gmail IMAP")

    email_ids = get_all_emails_having_unsubscibe_link(mails[0])
    set_of_links = get_all_emails_having_unsubscibe_link_threaded(mails, email_ids)

    with open('unsubscribe_links.txt', 'w') as file:
        for email, links in set_of_links.items():
            file.write(email + ':\n')
            for link in links:
                file.write(link + '\n')
            file.write('\n\n')

if __name__ == "__main__":
    main()
