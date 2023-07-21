# run_both.py
import subprocess

if __name__ == '__main__':
    flask_command = ['python', '-m', 'flask', 'run', '--port=4242', '--host=0.0.0.0']
    telegram_command = ['python', 'bot.py']


    flask_process = subprocess.Popen(flask_command)
    telegram_process = subprocess.Popen(telegram_command)

    flask_process.wait()
    telegram_process.wait()
