# Project set-up

First step is to clone the repository

```sh
git clone git@github.com:SergioHernandezRedondo/astd-project1.git
```

Then is necessary to create a virtual environment for python. We will do it with the next command:

```sh
# Change <your_venv_name> with the name you would like
python -m venv <your_venv_name>
```

We need to activate the created virtual environment. In my case I am using `fish` as my shell so we will use the next command:

```sh
source astd-venv/bin/activate.fish
```

Now let's install all the packages required

```sh
pip install -r requirements.txt
```

We can now launch the app using the following command:

```sh
python main/source/app.py
```
