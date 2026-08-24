# google-auth CLI reference

## Commands

```text
google-auth provider [--json]
google-auth accounts [--profile <app-profile>] [--auth] [--json]
google-auth login [--profile <app-profile>] [--json]
```

`provider` prints the declaration in `oauth-provider.json`; `--json` prints it verbatim. `accounts`
asks Rundesk which Google accounts it holds, which reads sealed local state and reaches no Google
API. `--auth` signs in first. `login` runs `rundesk login google` and then lists what is connected.
Errors go to stderr as `ERROR: <message>` with exit 2; nothing here ever prints a token, a client
value, or an authorization header.

`--profile` is only for an installation with more than one Google Cloud OAuth app — see below.
Leave it off unless you know you have two.

## What this package declares

Rundesk supplies the OAuth mechanics — browser, PKCE, token exchange, refresh, and the sealed grant
store — and reads Google's particulars from `oauth-provider.json`:

| Declared | Value |
|---|---|
| `authorization_endpoint` | `https://accounts.google.com/o/oauth2/v2/auth` |
| `token_endpoint` | `https://oauth2.googleapis.com/token` |
| `identity_endpoint` | `https://openidconnect.googleapis.com/v1/userinfo` |
| `identity` | `sub` is the durable account key; `email` is the human selector; `email_verified` must be true |
| `base_scopes` | `openid`, `https://www.googleapis.com/auth/userinfo.email` |
| `authorization_parameters` | `access_type=offline` for a refresh token, `prompt=consent select_account` so the account is chosen deliberately |
| `client_secret` | `true`: Google issues one even for a desktop client |
| `capabilities` | `analytics`, `search-console`, and `merchant`, each naming one Google scope |

A declaration may not set `client_id`, `redirect_uri`, `response_type`, `scope`, `state`,
`code_challenge`, or `code_challenge_method`: those belong to the mechanics and Rundesk refuses a
declaration that names them. Adding a Google API here means adding one capability and its scope, and
nothing else.

## Four different things, and confusing them is the usual failure

Setting Google up means getting four separate things right. They are easy to mistake for one
another, and each one fails with a different message:

| What | Where it is set | What goes wrong when it is missing |
|---|---|---|
| **API enablement** | Google Cloud console, per project | `403` naming the API and the project: "has not been used in project … or it is disabled" |
| **OAuth consent scopes** | Google Auth Platform → Data Access | the sign-in succeeds, then a call fails with "Request had insufficient authentication scopes" |
| **Resource permission** | Analytics, Search Console, Merchant Center themselves | the call succeeds and returns nothing, or `403` on that one property/site/account |
| **Account selection** | this catalog, at run time | "no Google account is connected", or a refusal listing the connected addresses |

Enabling an API does not grant a scope. Granting a scope does not give the person access to a
property. **The Google account that signs in must already have access to the Analytics properties,
Search Console sites, and Merchant Center accounts you intend to read** — Rundesk can only act as
that person, never above them.

## Set up the Google Cloud project

1. Use a dedicated Google Cloud project and enable only the APIs this installation will use:
   **Google Analytics Data API** and **Google Analytics Admin API** for Analytics, the **Search
   Console API**, and the **Merchant API** for Merchant Center. PageSpeed Insights is not part of
   this: it uses an API key and no sign-in at all.
2. Configure Google Auth Platform branding and audience. Internal suits a single eligible Workspace
   organization; otherwise choose External and add every intended account as a test user while the
   app is in Testing.
3. Under Data Access, declare `openid` and `https://www.googleapis.com/auth/userinfo.email` — which
   is how Rundesk establishes a verified,
   durable account identity — plus only the capability scopes this installation needs:

   | Capability | Scope | Why this one |
   |---|---|---|
   | `analytics` | `https://www.googleapis.com/auth/analytics.readonly` | read-only, and enough for every report this catalog runs |
   | `search-console` | `https://www.googleapis.com/auth/webmasters` | **not** the `.readonly` variant, because sitemap submission mutates; the read-only scope cannot submit one |
   | `merchant` | `https://www.googleapis.com/auth/content` | Google publishes exactly one Merchant API scope and it is read-write |

   Rundesk asks for `openid` and Google's canonical `userinfo.email` scope at sign-in and adds one
   capability scope only when a
   command first needs it, so an installation that never runs Merchant never consents to `content`.

4. Under Clients, create an OAuth client whose application type is **Desktop app**. Do not create a
   Web application client, and do not add a redirect URI.

   Rundesk's callback is a temporary loopback address, bound freshly for each sign-in:
   `http://127.0.0.1:<ephemeral-port>/<random-path>`. A Desktop app client permits that without any
   registered redirect URI, which is exactly why this is the right client type. Three details worth
   knowing before something looks wrong:

   - **`127.0.0.1`, not `localhost`.** Google matches a redirect as text, and that name can resolve
     to `::1`.
   - **No fixed port.** The port is chosen per sign-in, so there is nothing to register and nothing
     for another program on the machine to be holding. `rundesk login google` prints the exact
     address it is listening on before it opens the browser.
   - **No manual copy-and-paste.** Google's out-of-band flow, where a code is shown on a page for
     you to paste back, is retired and unsupported here. The browser has to be able to reach the
     loopback address on the same machine.

   After you approve, Google redirects to that address, the page says the authorization was
   received and to return to the terminal, and it closes itself a few seconds later. The command in
   the terminal is what reports the connected account.

5. Place the client values, then sign in:

   ```sh
   rundesk env set GOOGLE_OAUTH_CLIENT_ID
   rundesk env set GOOGLE_OAUTH_CLIENT_SECRET
   rundesk login google
   ```

   `rundesk env set` reads each value without echoing it; neither is ever passed as an argument.
   Do this while the Google Cloud console still has both on screen. `rundesk login google` then
   uses what is already stored and asks for nothing — and it asks only for a value that is
   genuinely missing, so having placed them first is the normal path, not a shortcut.

   Both values are sealed by Rundesk and withheld from every agent turn. **A skill process cannot
   read them**, which is why nothing in this catalog ever asks anyone for a client ID, a client
   secret, or a refresh token.

6. Connect more accounts by repeating `rundesk login google`. One Google Cloud OAuth app holds as
   many verified Google accounts as you sign in with; `--email` is how a command picks between
   them.

## More than one OAuth app: rarely, and explicitly

Almost every installation has one Google Cloud OAuth app and never types `--profile`. It exists for
the uncommon case of genuinely separate apps — a second Google Cloud project, or a client belonging
to someone else — and it suffixes the same value names:

```sh
rundesk env set GOOGLE_OAUTH_CLIENT_ID__ACME
rundesk env set GOOGLE_OAUTH_CLIENT_SECRET__ACME
rundesk login google --profile acme
```

`--profile` selects an **app**, never a person. Several Google accounts under one app is the
ordinary shape, and choosing between them is always `--email`.

## Merchant's scope is broader than the reading it does

Google publishes exactly one Merchant API scope and it is read-write. Constrain the signed-in
identity in Merchant Center instead, as `skills/google-merchant/references/cli.md` describes.

## When a grant stops working

An External consent screen left in **Testing** issues refresh tokens that expire in seven days for
these scopes; publish the app or expect to reconnect. Revocation, inactivity, Workspace policy, and
Google's per-account token limits can also end a grant. Every Google command here reports what
Rundesk refused and names the exact `rundesk login google` to repeat, with the profile when one is
in use.

## Validation

```sh
python3 skills/google-auth/scripts/google-auth.d/test-google-auth.py -q
skills/google-auth/scripts/google-auth --help
skills/google-auth/scripts/google-auth provider
```

Tests are offline: a stand-in Rundesk answers the bridge exactly as the real one documents it,
including its refusal of any response descriptor that is not a connected unnamed local socket.

## Official references

- [Google OAuth 2.0 for desktop apps](https://developers.google.com/identity/protocols/oauth2/native-app)
- [OpenID Connect on Google](https://developers.google.com/identity/openid-connect/openid-connect)
- [Google API scopes](https://developers.google.com/identity/protocols/oauth2/scopes)
