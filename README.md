# YATRA – Nepal Tourism Web App (Flask)

This folder is ready to open directly in **VS Code**.

## Quick start

1. Open this folder in VS Code.
2. Create a virtual environment (recommended):

   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Initialize the SQLite database:

   ```bash
   flask --app app.py init-db
   ```

5. (Optional) populate destinations with the SQL script:

   ```bash
   python
   >>> from app import db, app
   >>> from models import Destination
   >>> from sqlite3 import connect
   ```

   Or use a tool to execute `schema.sql` into `yatra.db`.

   Easiest: delete `yatra.db` if it exists, then:

   ```bash
   python -c "import sqlite3; db=sqlite3.connect('yatra.db'); db.executescript(open('schema.sql').read()); db.close()"
   ```

6. Run the app:

   ```bash
   flask --app app.py run
   ```

7. Browse to http://127.0.0.1:5000

Alternatively, press **Run and Debug** in VS Code and choose
**Python: Flask (YATRA)** from the debug configurations.
