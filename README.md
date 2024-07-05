# Gmail Unsubscribe Link Extractor

This script connects to a Gmail account via IMAP, searches for emails containing unsubscribe links, and extracts those links. It uses multithreading to speed up the process.

## Features

- Connects to Gmail using IMAP
- Searches for emails containing the word "unsubscribe"
- Extracts unsubscribe links from the email body and headers
- Uses multithreading for faster processing

## Installation

### Prerequisites

- Python 3.x
- A Gmail account with IMAP enabled

### Dependencies

Install the required Python packages using pip:

```sh
pip install -r requirements.txt
```

## Usage

1. **Set up your credentials file**:

   Create a `credentials.yaml` file in the same directory as the script. Add your Gmail username and password (or app password) to the file:

   ```yaml
   user: your_email@gmail.com
   password: your_password OR your_app_password
   ```

2. **Run the script**:

   Execute the script from the command line:

   ```sh
   python script_name.py
   ```

   OR

   ```sh
   python3 script_name.py
   ```

   The script will connect to Gmail, search for emails with unsubscribe links, and save the links to `unsubscribe_links.txt`.

### Credentials

Ensure your `credentials.yaml` file is correctly formatted with your Gmail credentials. The script will use this file to log in to your Gmail account.

### IMAP Settings

The script connects to `imap.gmail.com` by default. Ensure IMAP access is enabled in your Gmail settings.

## Contributing

Contributions are welcome! Please submit a pull request or open an issue to discuss your ideas.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.
