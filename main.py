# run_both.py
import subprocess

if __name__ == '__main__':
    flask_command = ['python','app.py']
    telegram_command = ['python', 'bot.py']


    flask_process = subprocess.Popen(flask_command)
    telegram_process = subprocess.Popen(telegram_command)

    flask_process.wait()
    telegram_process.wait()
