# Roadmap — VELLURÉ Marketplace

A multi-seller marketplace for second-hand / resale clothing, built on the
existing Django + SQLite backend.

---

## 1. What this project actually is

Two descriptions currently disagree, and it matters for every decision below.

| Source | Says |
|---|---|
| `README.md` | "buy & sell clothes website" |
| `templates/landing.html` | **VELLURÉ** — one luxury house, Paris, since 1974 |

The landing page is a pre-rendered React/Tailwind marketing site (SSR output,
`$tsr` router payload, hashed asset filenames). It is **not** a working shop:
`Cart (0)` is a hardcoded link to `#newsletter`, the newsletter form has no
action, and there is no product data anywhere.

**Decision (confirmed): this is a multi-seller marketplace.** VELLURÉ is the
storefront *brand*; the VELLURÉ copy becomes the default chrome, and anyone can
list clothes. So the build needs seller onboarding, moderation, and a payout
ledger — none of which a single-brand store would.

Keep the landing HTML. It is a good design. Reuse its typography (`Cormorant
Garamond` + `Jost`), the `bone`/`ink`/`gold` palette, and the `.btn-editorial`
/ `.eyebrow` classes as the design system for every new page.

---

## 2. Where the project is now

| Done | Status |
|---|---|
| Django 6.1.1 project | working |
| SQLite backend + migrations | working |
| Sign up / sign in | working, 10 tests passing |
| Session auth | working |
| Admin site | working |
| Landing page | static, SSR'd HTML, no data |

**Only 4 routes exist:** `/`, `/accounts/signup/`, `/accounts/signin/`, `/admin/`.

There is no product, cart, order, or seller code at all. Everything below is
greenfield.

### Known gaps to fix early

- `accounts/views.py` has no logout route. The old README promised one.
- Sign-up has no email verification and no password reset — both are needed
  before real users.
- Sign-in has no rate limiting. Add it before launch (see M3).
- `ALLOWED_HOSTS` is empty and `SECRET_KEY` is committed. Both must move to env
  vars before any deploy.
- The landing page's newsletter form posts nowhere; it needs CSRF protection if
  it ever becomes a real POST.

---

## 3. Milestones

Each milestone ends with something you can demo. Do not start a milestone until
the previous one is demoed.

---

### M1 — Profile and seller onboarding
*Foundation. Nothing else can be built without knowing who the seller is.*

1. Add `accounts.Profile` — `user` (OneToOne), `display_name`, `avatar`,
   `bio`, `city`, `created_at`. Register in `accounts/admin.py`.
2. `Profile` auto-creates via `post_save` signal on `User`.
3. Edit-profile page: `/accounts/profile/`.
4. Seller application: `SellerProfile` — `profile` (OneToOne), `status`
   (`pending` / `approved` / `rejected`), `legal_name`, `phone`, `id_document`,
   `submitted_at`, `reviewed_at`.
   - Vendors producing their own designs need proof they own the brand.
   - Resellers do not. Keep one `SellerProfile` with an optional
     `seller_type` field (`designer` / `reseller`) rather than two models.
5. `/sell/` landing page → application form.
6. Staff approval: a Django admin action on `SellerProfile` flips
   `pending → approved` and emails the applicant.
7. Permission helper: `seller_required` decorator, redirect to `/sell/` if the
   user has no approved `SellerProfile`.

**Done when:** a visitor can apply, an admin can approve, and only approved
sellers reach the listing form.

**Verify:** `python manage.py test accounts` still green.

---

### M2 — Listings and images

1. `marketplace` app: `python manage.py startapp marketplace`.
2. Models:
   - `Category` — `name`, `slug`, `parent` (self-FK, for Dresses / Outerwear / …).
   - `Size` — `name`, `order` (XS…XXL, One Size).
   - `Listing` — `seller` (FK `SellerProfile`), `title`, `description`,
     `category` (FK), `price` (Decimal, **store in toman or rial — decide once,
     never mix**), `condition` (`new` / `like_new` / `good` / `fair`),
     `status` (`draft` / `pending` / `live` / `sold` / `removed`),
     `created_at`, `updated_at`.
   - `ListingImage` — `listing` (FK, `related_name="images"`), `image`,
     `position`, `alt_text`.
   - `ListingSize` — through-table: which sizes this listing has, with
     `stock_count` per size. A dress in one size is not the same as one in five.
3. Price as `DecimalField(max_digits=10, decimal_places=0)` — **not** float.
   Float rounding on money is a real bug, not a style preference.
4. Image upload:
   - `ImageField` requires Pillow: add to `requirements.txt`.
   - `MEDIA_ROOT` / `MEDIA_URL` in settings; serve via `static()` in DEBUG only.
   - Validate uploads server-side: Pillow's `Image.verify()`, plus a max size
     and max megapixel cap. **Never trust `Content-Type` or the client.** A
     seller can upload anything.
   - Resize to a few widths (e.g. 400 / 800 / 1600px) and re-encode. Full-size
     uploads will be abused.
5. Listing form at `/sell/listings/new/` and `/sell/listings/<id>/edit/`.
6. Moderation: new listings land in `pending`. Admin approves → `live`.
   This protects buyers and is your defence against scams.
7. Public pages:
   - `/listing/<slug>/` — gallery, price, sizes, condition, seller card,
     "Buy" button.
   - `/search/` — filter by category, size, condition, price range; sort by
     newest / price.
8. Pagination on every list view. Django has a `Paginator`; no dependency needed.

**Done when:** an approved seller can list a garment with photos, it passes
moderation, a visitor can find it via search, and the detail page renders.

---

### M3 — Cart and orders

1. **Cart:** session-keyed for guests, merged into a `Cart` row on login.
   - `Cart` — `user` (OneToOne), `updated_at`
   - `CartItem` — `cart` (FK), `listing` (FK), `size` (FK `Size`), `quantity`
   - `unique_together` on `(cart, listing, size)` so a row cannot duplicate.
2. Guest cart in `request.session["cart"]`; on login, merge and delete. Sellers
   on Iranian gateways often have buyers on different devices — session carts
   are the common case, so this path gets tested hard.
3. `/cart/` page, with stock checks at add-time *and* at checkout.
4. `Order` — `buyer` (FK), `status`, `total`, `created_at`, `shipping_*`,
   `placed_at`.
   - `OrderItem` — `order` (FK), `listing` (FK), `size`, `unit_price`,
     `seller` (FK, denormalised). **Copy the price onto the order item.** If
     you read price from `Listing` later, a seller editing their price silently
     rewrites your order history.
5. State machine, enforced by a method that validates transitions rather than
   scattered `if` statements:

   ```
   pending_payment → paid → shipped → delivered → completed
          ↓             ↓
       cancelled      refunded
   ```

6. `/checkout/` → `/orders/<id>/`.
7. Buyer order history: `/orders/`.
8. Throttling: `@ratelimit` (django-ratelimit, one small dep) on sign-in,
   sign-up, and checkout.

**Done when:** buyer can add to cart, check out, and see an order in a state the
seller can act on.

**No payment yet** — M3 ends with orders in `pending_payment`. That is the
right order of work; see M4.

---

### M4 — Payments and the payout ledger

**This is the highest-risk milestone. Read this section before writing code.**

#### The constraint

You mentioned Iranian hosting. That has a hard consequence:

> **Stripe is not available in Iran, so Stripe Connect is not available.**
> Connect is what splits one buyer payment across many sellers and pays each one
> out. Without it you must build the ledger and the split yourself.

Do not plan around Stripe Connect. Plan around a ledger, and it will also work
if you later add Stripe — the model is the same shape.

#### Verify before you build

Gateway specifics change and I could not confirm current status. Before writing
any integration, check directly:

- Which gateway you can actually get a merchant account with (Zarinpal,
  IDPay, Mellat, Zibal, or another) and **what settlement model it uses**.
- Whether it supports **split payouts to sub-merchants** (this is the question
  that decides everything).
- Whether it accepts **international cards**.
- Iranian gateways typically settle to **one bank account you control**. That
  means *you* hold buyer money temporarily and owe sellers later. That is a
  money-holding and money-transmission situation with legal weight — get advice
  before real volume, and read the gateway's terms.

#### Design the ledger either way

`LedgerEntry` — `order` (FK), `seller` (FK), `kind` (`charge` / `refund` /
`commission` / `payout`), `amount` (Decimal), `created_at`.
Plus `SellerBalance` — `seller` (OneToOne), `available`, `pending`, `updated_at`.

Compute: `available` = charges − commission − refunds − payouts.

Never store a "seller earned" number. Store entries and derive the balance.
A derived balance cannot drift out of sync with its own history.

#### Two viable shapes

| | **Escrow-lite** | **Gateway split** |
|---|---|---|
| Buyer pays | You, one charge | Gateway, split at checkout |
| Payout to seller | You transfer, manually, later | Gateway pays seller directly |
| You hold money | **Yes**, temporarily | No |
| Legal exposure | Higher | Lower |
| Build effort | Ledger only | Gateway-specific integration |
| Works if gateway changes | Yes | No |
| Best for | Low volume, few sellers, offline settlement | Higher volume, many sellers |

**Recommendation: build Escrow-lite for launch.** It works with any Iranian
gateway, needs no per-seller onboarding with the gateway, and is the smaller
build. Do not hand out money automatically until the ledger is proven. Have an
admin trigger payouts by hand, with a payout record each time.

If you cannot legally hold buyer funds, go straight to a gateway with split
support — confirm it exists for your account before committing.

#### Commission

`settings.py`:

```python
MARKETPLACE_COMMISSION_RATE = Decimal("0.10")  # 10%
```

Buyer pays price + shipping; seller receives price × (1 − rate). Show the
commission to sellers on the dashboard *before* they list. Changing it later
and telling them afterwards is the fastest way to lose sellers.

#### Stripe alternative (if you operate outside Iran)

Keep `LedgerEntry` as the source of truth and add Stripe Connect as another
settlement channel on top. One ledger, many rails. This is why the ledger is
built first.

**Done when:** a real order moves `pending_payment → paid`, the ledger balances,
and a seller sees a balance.

---

### M5 — Seller dashboard
*Where sellers actually live. Budget real time here.*

1. `/dashboard/` — listings (with edit/delete), orders to fulfil, balance,
   pending payouts, payout history.
2. Edit and pause listings.
3. Mark shipped, enter a tracking number.
4. Request payout; admin approves; `payout` ledger entry written.
5. Simple stats: views, items sold, earnings over time.
6. Email on: sale, order shipped, payout sent.

**Done when:** a seller can run their whole side without you.

---

### M6 — Deploy

**SQLite does not survive a normal deploy.** It is a single file on local disk.
The moment you run two instances, or the platform gives you an ephemeral
filesystem, your data is gone or split. Switch to Postgres at M6 — or earlier if
you deploy anything.

Make settings read from the environment, and add `dj-database-url` (one small
dependency) so the same code runs locally and in production:

```python
import os
import dj_database_url

SECRET_KEY = os.environ["DJANGO_SECRET_KEY"]
DEBUG = os.environ.get("DJANGO_DEBUG", "0") == "1"
ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS", "").split(",")

DATABASES = {"default": dj_database_url.config(default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}")}
```

That keeps SQLite as the zero-setup local default and adds Postgres in prod with
no branching elsewhere. `manage.py check --deploy` must pass with zero warnings.

**Media files** cannot live in git or on the app filesystem — the deploy will
wipe them. Use object storage (S3, or the platform's equivalent) from day one
of deploy, via `django-storages`.

#### Hosting options

| | PaaS (Render / Railway / Fly) | Iranian hosts | VPS |
|---|---|---|---|
| Effort | Lowest | Medium | Highest |
| Managed Postgres | Yes | Varies | You install it |
| Custom domain | Yes | Varies | Yes |
| HTTPS | Automatic | Often manual | certbot |
| Payment gateway reach | Varies | Usually best | Depends on region |

On Iranian hosts, expect to configure Nginx, a process manager (systemd or
supervisor), and certificates by hand. Confirm each host's support for your
gateway and for Postgres before committing.

### M7 — Hardening before real users

Work through `python manage.py check --deploy` until it is silent.

- [ ] `DEBUG=False`, env-var `SECRET_KEY`, `ALLOWED_HOSTS` set
- [ ] `SECURE_SSL_REDIRECT`, `SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE`
- [ ] `SECURE_HSTS_SECONDS`
- [ ] Email verified sign-up + password reset
- [ ] Throttling on sign-in, sign-up, checkout, listing creation
- [ ] Backups, with a restore actually tested
- [ ] File-upload limits enforced, and hostile uploads tested
- [ ] CSRF on every POST, including the newsletter form
- [ ] Logging, with something that alerts on 5xx

Then, if you want it: search relevance, saved favourites, reviews, seller
ratings, notifications, i18n (`LANGUAGE_CODE` is `en-us` — `USE_I18N` is already
on), PWA, and SEO/analytics.

---

## 4. Data model, all at once

So you can see the shape of the finished system:

```
User ──1:1── Profile ──1:1── SellerProfile (status)
                             │
                             ├──< Listing ──< ListingImage
                             │      │
                             │      └──< ListingSize >── Size
                             │             └── stock_count
                             │
                             └──< LedgerEntry (charge/refund/commission/payout)

Category (self-FK tree)

Cart ──< CartItem >── Listing + Size

Order (buyer) ──< OrderItem (listing, size, seller, unit_price snapshot)
```

Note the two deliberate denormalisations: `OrderItem.unit_price` and
`OrderItem.seller` are copied at purchase time. Both are history-preserving —
editing a listing must never rewrite a past order.

---

## 5. Risk register

| Risk | Impact | Mitigation |
|---|---|---|
| **Money handling** | Legal, financial | Escrow-lite only, ledger-derived balances, manual payouts at first, get advice before volume |
| **SQLite on deploy** | Data loss | Postgres from M6, managed backups |
| **Uploaded files** | Storage blowout, abuse | Resize on upload, cap size + megapixels, object storage, never trust the client |
| **Payment gateway changes** | Rewrite | Ledger decoupled from any one gateway |
| **No email** | Users locked out | Add sending in M1, not at the end |
| **Building search too early** | Wasted weeks | `icontains` and filters are fine to real volume. Revisit at ~50k listings |
| **Not shipping M1–M3** | Nothing usable | Demo each milestone before starting the next |

---

## 6. Suggested order

```
M1 Profile & seller onboarding   ← foundation
M2 Listings & images            ← the product
M3 Cart & orders                ← the transaction
M4 Payments & ledger             ← the money (highest risk)
M5 Seller dashboard             ← seller retention
M6 Deploy                       ← go live
M7 Harden                       ← real users
```

M1–M3 need no payment gateway and no hosting decisions, so they can be built
entirely offline. Start there.

---

## 7. Open decisions

Answer these before M4 — each one changes the build:

1. **Which gateway?** Which merchant account can you actually get?
2. **Does it support sub-merchant splits?** Decides escrow vs. split.
3. **Can you legally hold buyer funds temporarily?**
4. **Currency and unit** — toman or rial, displayed price vs. settlement price.
5. **Commission rate**, and whether the seller or buyer pays it.
6. **Shipping** — flat rate, or seller-calculated per listing?
7. **Which countries?** Affects currency, tax, and whether the Iranian gateway
   is even the right choice.