import os
import sys
import yaml

def extract_emails_from_yml(folder_path, excluded_files):
    emails = []

    for filename in os.listdir(folder_path):
        if not filename.endswith('.yml') or filename in excluded_files:
            continue

        file_path = os.path.join(folder_path, filename)
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = yaml.safe_load(file)
                contributors = content.get('model_contributors', [])
                for contributor in contributors:
                    email = contributor.get('email')
                    if email:
                        emails.append(email)
        except Exception as e:
            print(f"Errore nella lettura del file {filename}: {e}")

    return emails

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python script.py <folder_path> <excluded_file1> <excluded_file2> ...")
        sys.exit(1)

    folder = sys.argv[1]
    excluded = sys.argv[2:]

    emails = extract_emails_from_yml(folder, excluded)
    print("\n".join(emails))
