+++
id = "frontend.nextjs"
title = "Next.js"
severity = "preferred"
scopes = ["frontend"]
+++
# Next.js

- For greenfield full web applications when no frontend framework was selected, prefer current stable Next.js + React.
- Never migrate an existing Vue/Svelte/SPA/server-rendered stack to Next.js without explicit user approval.
- Choose server/client boundaries based on data ownership, caching, SEO, and interaction needs rather than making everything client-side.
