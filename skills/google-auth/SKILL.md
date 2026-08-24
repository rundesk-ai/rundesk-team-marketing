---
name: google-auth
description: Use when a Google skill in this catalog reports that no Google account is connected, that a grant was revoked or a scope is missing, or that an account choice is ambiguous; when the user asks to connect, list, choose, or re-authorize a Google account for Rundesk; or when setting up the Google Cloud project, APIs, consent scopes, and Desktop OAuth client these skills sign in with. It supplies the catalog's Google provider definition and the sign-in commands the other Google skills depend on. Do not use it to read Analytics, Search Console, Merchant Center, or PageSpeed data.
---

# Google sign-in

Rundesk owns Google sign-in for this catalog. This package owns the definition Rundesk reads —
Google's endpoints, identity fields, base scopes, and one scope per capability — in
`oauth-provider.json` beside this file. It holds no client, no grant, and no OAuth code, and the
other Google skills read nothing from it and never run it.

```sh
"$RUNDESK_SKILLS/google-auth/scripts/google-auth" provider
"$RUNDESK_SKILLS/google-auth/scripts/google-auth" accounts
"$RUNDESK_SKILLS/google-auth/scripts/google-auth" login
```

`provider` reports what this catalog declares Google to be and contacts nobody. `accounts` lists the
Google accounts Rundesk holds and reaches no Google API. `login` runs Rundesk's own browser sign-in
and then shows what it connected.

One Google Cloud OAuth app holds as many verified Google accounts as the owner signs in with. Every
data skill here takes `--email <address>` to pick the account, needed only when Rundesk holds more
than one.

**Never ask anyone for a client ID, client secret, or refresh token, and never accept one.** The
owner places the app client themselves with `rundesk env set GOOGLE_OAUTH_CLIENT_ID` and
`rundesk env set GOOGLE_OAUTH_CLIENT_SECRET`, and Rundesk seals both and withholds them from every
agent turn — a skill process cannot read them, and does not need to.

When a Google skill says nothing is connected, run `accounts` to see what exists, then ask the owner
to run `rundesk login google` in their own terminal. Use `login` here only when a browser is
available to whoever is running this.

`--profile <app-profile>` exists on these commands and on every data skill, and is almost never
right: it selects a second OAuth **app**, for the uncommon installation with two Google Cloud
projects.
Do not offer it, do not add it to a command you are constructing, and do not treat it as the way to
choose an account — that is always `--email`. Read `references/cli.md` before using it.

Read `references/cli.md` before advising on setup. It separates the four things people confuse —
enabling APIs, consenting to scopes, holding permission on the Google resources themselves, and
selecting an account at run time — and covers the Desktop-app client type, the loopback callback,
the scope each capability carries, and what to do when a grant expires or is revoked.
