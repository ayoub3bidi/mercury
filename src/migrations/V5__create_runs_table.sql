CREATE TABLE public.runs (
    id UUID PRIMARY KEY,
    idempotency_key VARCHAR(255) NOT NULL UNIQUE,
    prompt TEXT NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'queued',
    token_budget INTEGER NOT NULL,
    result TEXT,
    error TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT runs_status_check CHECK (status IN ('queued', 'running', 'completed', 'failed')),
    CONSTRAINT runs_token_budget_check CHECK (token_budget > 0)
);
