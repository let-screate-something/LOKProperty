# LOK Property Solutions

Real estate website for selling plots and houses.

```
lok-property/
├── server/        Python Flask API + SQLite database      (done)
├── admin-site/    Admin website: plain HTML / CSS / JS    (done)
└── public-site/   Website for visitors                    (done)
```

## How it works

```
 Admin site (login) ─┐
                     ├──>  Flask API  ──>  SQLite database
 Public site (none) ─┘     /api/admin/*  needs login token
                           /api/*        open for visitors (read + send enquiry)
```

## Run it on your computer

You need Python 3.10 or newer.

### 1. Start the server
```bash
cd server
pip install -r requirements.txt
python create_admin.py          # asks for an admin username and password
python app.py                   # API runs on http://localhost:5000
```
The database file (`lok_property.db`) is created automatically on first run.
Check it works: open http://localhost:5000/api/health

### 2. Seed demo data (optional)
```bash
python seed_demo.py
```
Adds 8 demo properties (plots and houses, 2 already sold with buyer records).
Safe to run multiple times — it skips properties that already exist.

### 3. Start the admin site
In a second terminal:
```bash
cd admin-site
python -m http.server 8000
```
Open http://localhost:8000/login.html and log in with the account from step 1.

### 4. Start the public website
In a third terminal:
```bash
cd public-site
python -m http.server 8001
```
Open http://localhost:8001/index.html

## What the admin can do
- Add, edit and delete plots and houses
- Mark a property **Sold**: a pop-up asks for buyer name, email, phone and final price,
  and saves it as a **sales record**
- Mark it **Available** again (the sale record is removed, to undo mistakes)
- See visitor enquiries and all sales records
- A property with a sale record cannot be deleted, so buy records are never lost

## What the public site has
- Home page with featured available properties
- Listings page with filters (type, status, city search)
- Property detail page with photos and "Send Enquiry" button
- Contact page with enquiry form + phone/WhatsApp/email/address
- About page

## Email notifications
When a visitor sends an enquiry, the server tries to email it to you.

To enable, set these environment variables before starting the server:
- `MAIL_USER` — your Gmail address
- `MAIL_PASSWORD` — your Gmail app password (not your regular password)
- `MAIL_TO` — where enquiries should be sent (can be same as MAIL_USER)

Example:
```bash
set MAIL_USER=yourname@gmail.com
set MAIL_PASSWORD=your-app-password
set MAIL_TO=yourname@gmail.com
python app.py
```

**Gmail app password setup:**
1. Go to your Google Account → Security → 2-Step Verification (turn it on)
2. Go to Security → App passwords → select "Mail" and your device → copy the 16-character password
3. Use that app password as `MAIL_PASSWORD` (not your regular Gmail password)

If the variables are missing or sending fails, the enquiry is still saved and the
visitor still sees "Thank you!" — the server never crashes.

## API list

| Route | Who | What it does |
|---|---|---|
| `GET /api/properties` | anyone | List properties. Filters: `type`, `city`, `min_price`, `max_price`, `status`, `sort` |
| `GET /api/properties/<id>` | anyone | One property with photos |
| `POST /api/enquiries` | anyone | Visitor sends name + email + message (email notification sent) |
| `POST /api/admin/login` | admin | Returns a login token |
| `GET /api/admin/stats` | admin | Dashboard numbers |
| `GET/POST /api/admin/properties` | admin | List all / add |
| `GET/PUT/DELETE /api/admin/properties/<id>` | admin | View / edit / delete |
| `PATCH /api/admin/properties/<id>/status` | admin | Mark sold or available |
| `GET/DELETE /api/admin/enquiries` | admin | View / delete enquiries |
| `GET /api/admin/sales` | admin | Buy records |

## Settings (environment variables)

| Name | Meaning | Default |
|---|---|---|
| `SECRET_KEY` | Signs login tokens. **Set a long random value online.** | development key |
| `DB_PATH` | Where the database file is stored | `server/lok_property.db` |
| `TOKEN_HOURS` | How long an admin stays logged in | `8` |
| `CORS_ORIGINS` | Websites allowed to call the API, comma separated | `*` (anyone) |
| `PORT` | Server port | `5000` |
| `DEBUG` | `1` = auto-restart on code changes. Use `0` online. | `1` |
| `MAIL_USER` | Gmail address for enquiry emails | (none) |
| `MAIL_PASSWORD` | Gmail app password for enquiry emails | (none) |
| `MAIL_TO` | Recipient address for enquiry emails | (none) |

## Before going online (checklist)
1. Set a strong `SECRET_KEY`.
2. Set `CORS_ORIGINS` to your real website addresses.
3. Run with `DEBUG=0` using a production server such as `gunicorn app:app`.
4. Change `API_URL` in `admin-site/js/config.js` and `public-site/js/config.js` to the online server address.
5. Replace `!!PLACEHOLDER!!` address in `public-site/js/config.js` with your real office address.
6. **Database:** free hosts (like Render) wipe local files when the server restarts,
   so SQLite is for your computer only. Online, use a free PostgreSQL (Neon or Supabase).
   Only `server/db.py` and `server/schema.sql` need to change for that.
7. Use HTTPS (the hosts above give it for free).
8. Set up `MAIL_USER`, `MAIL_PASSWORD`, `MAIL_TO` for enquiry email notifications.

## Next steps
- Photo upload with Cloudinary (right now photos are added as links)
- Online hosting (Render, Railway, etc.)
