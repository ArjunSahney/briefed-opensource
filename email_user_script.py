import sys
import subprocess
from datetime import datetime
from morning_brieifing import in_morning_brief

def main(name, email, date, interest1, interest2, interest3):
    # Execute the morning briefing function
    in_morning_brief(name, interest1, interest2, interest3)
    
    # Use the provided date or the current date if not specified
    date_str = datetime.now().strftime('%Y-%m-%d')
    
    # Construct the file name
    file_name = f"brief_files/email_dict_{name}_{date_str}.txt"
    
    # Verify the file exists before attempting to send it
    try:
        with open(file_name, 'r'):
            pass  # File exists and is readable, proceed with sending email
    except FileNotFoundError:
        print(f"Error: The file {file_name} does not exist.")
        return

    # Construct and execute the command to send the email
    command = ["node", "email_send.js", file_name, email]
    try:
        # Execute the command and capture the output
        result = subprocess.run(command, check=True, text=True, capture_output=True)
        print(result.stdout)  # Output the result from the Node.js script
    except subprocess.CalledProcessError as e:
        print(f"An error occurred: {e.stderr}")

if __name__ == "__main__":
    if len(sys.argv) < 7:
        print("Usage: python script.py name email date interest1 interest2 interest3")
    else:
        main(*sys.argv[1:])
