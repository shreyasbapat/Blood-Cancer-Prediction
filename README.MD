# This app is written in Python3.<br>

Extra css file and js should be kept in `/static` folder.<br>

# Usb Camera Integration
Install motion daemon on your rpi.
>sudo apt-get install motion

Before running the flask app make sure `motion daemon is running` or you can restart it by
>sudo service motion restart

You can check if it is running on `http://localhost:8081`

Once it is running, then run the flask app as explained below.

## Install Dependencies
All dependencies are listed in `requirements.txt`. Install those before proceeding furthur.<br>

## Running the app

> python3 app.py

Then open `http://localhost:5001/` in your browser.



## Motor Code

Just create a method
>import motor1

>motor1.setup(Motor=#Pin No)

>motor1.run(Motor=#Pin No)

>return bla bla
