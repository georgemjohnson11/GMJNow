# GMJNow
This is the code (without static images) for the website gmjnow.com

## Installation

Use [Docker](https://docs.docker.com/get-docker/) or the package manager [pip](https://pip.pypa.io/en/stable/) to get up and running.

If docker is installed, besides running some automation to get data, you'll need to following to get the App up and running

```bash
docker build -t gmjnow .
docker run -d -p 8000:8000  \
--mount type=bind,source="/${pwd}/stock_dfs/",target=/app/stock_dfs,readonly \
--mount type=bind,source="/${pwd}/static/",target=/app/static,readonly \
--name finance-app gmjnow
```

You'll need a postgres server to run the blog and can connect through the settings
```bash
pip3 install -r requirements.txt
python3 manage.py migrate
python3 manage.py runserver 127.0.0.1:8000
```

1. Clone this Repository
2. In the root directory source the bin file i.e. (source bin/activate) in your bash CLI)
3. installing pip https://pip.pypa.io/en/stable/installing/
4. Run 'pip3 install -r requirements.txt' in the root directory of this project
5. Run 'python3 manage.py migrate'
6. Run 'python3 manage.py runserver 127.0.0.1:8000'
7. Go in your browser to '127.0.0.1:8000'


## Deploying   
The nginx.conf can be dropped in `/etc/nginx/conf.d/` and should serve up traffic if you insert your domain approopriately and get SSL certs on the EC2 instance
Docker command:   
`docker run -d -p 8000:8000  \
--mount type=bind,source="/${pwd}/stock_dfs/",target=/app/stock_dfs,readonly \
--mount type=bind,source="/${pwd}/static/",target=/app/static,readonly \
--name finance-app gmjnow`   
   

##TO DO   
8. Save Model using [Mongo DB](https://django-mongodb-engine.readthedocs.io/en/latest/tutorial.html)
6. Change static file asset hosting
5. Separate AI from basic information
7. Add Testing
4. Add Finance Postgres model Backend Find models from C# Project
7. Use Airflow instead of cron jobs to schedule tasks
3. Start React frontend - make more modular
2. Utilize simpleAnalysis and positions app
1. Use mixins to simplify Setup


## License
[MIT](https://choosealicense.com/licenses/mit/)