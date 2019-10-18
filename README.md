# Profile Masker

## Development
- `pip install -r requirements.txt`
- `export FLASK_DEBUG=True`
- `flask run`

## Deployment

### Heroku
- Add `https://github.com/heroku/heroku-buildpack-apt` to your application's buildpack
- so it will install the packages in Aptfile
