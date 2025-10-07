[Create a new repo from template](https://github.com/new?template_name=hello-codespeak&template_owner=codespeak-dev)
  - repo name
  - visibility: public (private is OK)


# 🔴 Now continue in the new repo

The following instructions are copied to the new repo

----



# Set up the CodeSpeak Build Process

- [Edit spec](../../edit/main/spec/main.cs.md)
  - commit
- [New Secret](../../settings/secrets/actions/new)
  - `ANTHROPIC_API_KEY`
  - https://console.anthropic.com/settings/keys
- [Install CodeSpeak App](https://github.com/apps/codespeak-build)
  - [Check](../../settings/installations)
- Look at the [last commit](../../commit/HEAD)
  - or [Commit history for main.cs.md](../../commits/main/spec/main.cs.md)
  - see checks' status

### Code Change Requests
- [Change request](../../new/main?filename=change-request.cs.md&value=Describe%20your%20change%20request%20here)

# Run the app

Locally
  - clone/pull locally
    - `git clone ...`
    - `git pull ...`

Remotely with GitHub Codespaces
  - use codespaces
  - [install uv](https://docs.astral.sh/uv/getting-started/installation/)
    - `curl -LsSf https://astral.sh/uv/install.sh | sh`

## Prepare and run
- `uv sync`
- `uv run python manage.py migrate`
- `uv run python manage.py runserver`
- open [http://localhost:8000](http://localhost:8000)

# Deploy with render.com
- create an account at render.com
- [create Web Service](https://dashboard.render.com/web/new)
- plug in public github url
- make sure language is `Python 3`
- build command: `uv sync --frozen && uv cache prune --ci && uv run manage.py migrate`
  - you can do `uv run manage.py migrate` in Advanced/pre-deploy command instead
- start command: `uv run manage.py runserver 0.0.0.0:$PORT` (this is a dev server, for prod deploments use `gunicorn`)
- choose Instance type: `Free`
- env var: `ALLOWED_HOSTS`, value: `*`
- env var `CSRF_TRUSTED_ORIGINS`: `https://*.onrender.com`

### DE on Render.com
- [Create new Postgres DB](https://dashboard.render.com/new/database)
- choose Free instance
- copy internal connection URL
- prepend `uv add psycopg2-binary && ` to build command:
  - `uv add psycopg2-binary && uv sync --frozen && uv cache prune --ci && uv run manage.py migrate`
