# Customer Support Agent: Documentation Suite

Welcome to the official technical documentation for the **Customer Support Agent with LangGraph**.

This documentation suite provides a complete, granular reference for software engineers, architects, DevOps engineers, and technical evaluators who want to understand, operate, extend, or present this Agentic AI platform.

---

## 📚 Documentation Index

| Document | Description |
| :--- | :--- |
| **[Master Documentation (`FULL_PROJECT_DOCUMENTATION.md`)](./FULL_PROJECT_DOCUMENTATION.md)** | The complete all-in-one guide covering business value, architecture, code walkthrough, workflows, HITL, deployment, and presentation cheat sheets. |
| **[System Architecture (`ARCHITECTURE.md`)](./ARCHITECTURE.md)** | In-depth breakdown of the 3-tier architecture, LangGraph parent state machine, typed state schema (`SupportState`), reducers, and dual-backend checkpointer design. |
| **[Workflows & Domain Subgraphs (`WORKFLOWS.md`)](./WORKFLOWS.md)** | Granular analysis of the 4 specialized subgraphs (Billing, Technical, Account, General), hybrid classification, and slot-based multi-entity tracking. |
| **[Human-in-the-Loop Guide (`HUMAN_IN_THE_LOOP.md`)](./HUMAN_IN_THE_LOOP.md)** | Deep dive into native LangGraph `interrupt()` execution, snapshot persistence across server restarts, and `/support/resume` with `Command(resume=...)`. |
| **[API Reference (`API_REFERENCE.md`)](./API_REFERENCE.md)** | Complete specification of all REST endpoints, JWT authentication, request/response JSON schemas, error handling, and thread isolation. |
| **[Deployment & DevOps (`DEPLOYMENT_AND_DEVOPS.md`)](./DEPLOYMENT_AND_DEVOPS.md)** | Production deployment guide covering multi-platform Docker (`amd64`/`arm64`), GitHub Actions CI/CD, Render Web Services, Neon PostgreSQL, and cold-start resilience. |

---

## 🚀 Quick Links
- **Live Frontend**: [https://customer-support-agent-frontend.onrender.com](https://customer-support-agent-frontend.onrender.com)
- **Live Backend API**: [https://customer-support-agent-4960.onrender.com](https://customer-support-agent-4960.onrender.com)
- **Interactive Swagger Docs**: [https://customer-support-agent-4960.onrender.com/docs](https://customer-support-agent-4960.onrender.com/docs)
- **Docker Hub API Image**: [amankhan1009/customer-support-agent-api](https://hub.docker.com/r/amankhan1009/customer-support-agent-api)
- **Docker Hub Frontend Image**: [amankhan1009/customer-support-agent-frontend](https://hub.docker.com/r/amankhan1009/customer-support-agent-frontend)
