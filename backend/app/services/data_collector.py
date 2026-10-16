import logging
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import requests
from sqlalchemy.orm import Session

from backend.app.config import settings
from backend.app.models import Developer, Repository, Issue, Interaction

logger = logging.getLogger(__name__)

# Curated catalog of top open-source repositories across multiple languages
SEED_REPOSITORIES = [
    # Python
    {
        "owner": "tiangolo", "name": "fastapi", "full_name": "tiangolo/fastapi",
        "language": "Python", "topics": "fastapi,api,python,asyncio,pydantic,web",
        "description": "FastAPI framework, high performance, easy to learn, fast to code, ready for production",
        "stars_count": 78200, "forks_count": 6400, "open_issues_count": 420,
        "url": "https://github.com/tiangolo/fastapi"
    },
    {
        "owner": "psf", "name": "requests", "full_name": "psf/requests",
        "language": "Python", "topics": "http,requests,python,networking,client",
        "description": "A simple, yet elegant, HTTP library for Python.",
        "stars_count": 52100, "forks_count": 9200, "open_issues_count": 180,
        "url": "https://github.com/psf/requests"
    },
    {
        "owner": "pytorch", "name": "pytorch", "full_name": "pytorch/pytorch",
        "language": "Python", "topics": "machine-learning,deep-learning,pytorch,gpu,neural-network,ai",
        "description": "Tensors and Dynamic neural networks in Python with strong GPU acceleration",
        "stars_count": 89400, "forks_count": 23500, "open_issues_count": 1400,
        "url": "https://github.com/pytorch/pytorch"
    },
    {
        "owner": "huggingface", "name": "transformers", "full_name": "huggingface/transformers",
        "language": "Python", "topics": "nlp,llm,transformers,deep-learning,pytorch,huggingface,bert,gpt",
        "description": "State-of-the-art Machine Learning for Pytorch, TensorFlow, and JAX.",
        "stars_count": 138000, "forks_count": 26900, "open_issues_count": 850,
        "url": "https://github.com/huggingface/transformers"
    },
    {
        "owner": "pallets", "name": "flask", "full_name": "pallets/flask",
        "language": "Python", "topics": "flask,python,web,framework,wsgi,microframework",
        "description": "The Python micro framework for building web applications.",
        "stars_count": 68400, "forks_count": 16200, "open_issues_count": 65,
        "url": "https://github.com/pallets/flask"
    },
    {
        "owner": "scikit-learn", "name": "scikit-learn", "full_name": "scikit-learn/scikit-learn",
        "language": "Python", "topics": "machine-learning,scikit-learn,data-science,python,statistics",
        "description": "Machine Learning in Python. Simple and efficient tools for predictive data analysis.",
        "stars_count": 60500, "forks_count": 25800, "open_issues_count": 2100,
        "url": "https://github.com/scikit-learn/scikit-learn"
    },
    {
        "owner": "pola-rs", "name": "polars", "full_name": "pola-rs/polars",
        "language": "Rust", "topics": "polars,dataframe,rust,python,data-engineering,arrow",
        "description": "Fast multi-threaded, hybrid-streaming DataFrame library in Rust and Python",
        "stars_count": 32000, "forks_count": 2100, "open_issues_count": 480,
        "url": "https://github.com/pola-rs/polars"
    },
    # TypeScript / JavaScript
    {
        "owner": "facebook", "name": "react", "full_name": "facebook/react",
        "language": "TypeScript", "topics": "react,javascript,ui,frontend,declarative,virtual-dom",
        "description": "The library for web and native user interfaces.",
        "stars_count": 232000, "forks_count": 46900, "open_issues_count": 1200,
        "url": "https://github.com/facebook/react"
    },
    {
        "owner": "vercel", "name": "next.js", "full_name": "vercel/next.js",
        "language": "TypeScript", "topics": "nextjs,react,ssr,fullstack,jamstack,typescript",
        "description": "The React Framework for the Web.",
        "stars_count": 128000, "forks_count": 27100, "open_issues_count": 2400,
        "url": "https://github.com/vercel/next.js"
    },
    {
        "owner": "tailwindlabs", "name": "tailwindcss", "full_name": "tailwindlabs/tailwindcss",
        "language": "TypeScript", "topics": "css,tailwindcss,design-system,frontend,utility-first",
        "description": "A utility-first CSS framework for rapid UI development.",
        "stars_count": 84500, "forks_count": 4300, "open_issues_count": 110,
        "url": "https://github.com/tailwindlabs/tailwindcss"
    },
    {
        "owner": "shadcn-ui", "name": "ui", "full_name": "shadcn-ui/ui",
        "language": "TypeScript", "topics": "react,tailwind,radix-ui,components,design-system",
        "description": "Beautifully designed components that you can copy and paste into your apps.",
        "stars_count": 75000, "forks_count": 6800, "open_issues_count": 310,
        "url": "https://github.com/shadcn-ui/ui"
    },
    {
        "owner": "microsoft", "name": "vscode", "full_name": "microsoft/vscode",
        "language": "TypeScript", "topics": "vscode,editor,developer-tools,electron,typescript",
        "description": "Visual Studio Code - Code editing. Redefined.",
        "stars_count": 164000, "forks_count": 31000, "open_issues_count": 5400,
        "url": "https://github.com/microsoft/vscode"
    },
    # Rust
    {
        "owner": "tokio-rs", "name": "tokio", "full_name": "tokio-rs/tokio",
        "language": "Rust", "topics": "tokio,async,rust,runtime,networking,io",
        "description": "A runtime for writing reliable, asynchronous, and slim applications with the Rust programming language.",
        "stars_count": 27800, "forks_count": 2500, "open_issues_count": 290,
        "url": "https://github.com/tokio-rs/tokio"
    },
    {
        "owner": "rust-lang", "name": "cargo", "full_name": "rust-lang/cargo",
        "language": "Rust", "topics": "rust,cargo,package-manager,build-tool,cli",
        "description": "The Rust package manager and build tool.",
        "stars_count": 13400, "forks_count": 2400, "open_issues_count": 680,
        "url": "https://github.com/rust-lang/cargo"
    },
    {
        "owner": "hyperium", "name": "hyper", "full_name": "hyperium/hyper",
        "language": "Rust", "topics": "rust,http,networking,server,client,async",
        "description": "An HTTP library for Rust. Fast and correct.",
        "stars_count": 14200, "forks_count": 1500, "open_issues_count": 140,
        "url": "https://github.com/hyperium/hyper"
    },
    # Go
    {
        "owner": "gin-gonic", "name": "gin", "full_name": "gin-gonic/gin",
        "language": "Go", "topics": "gin,go,golang,web,framework,router,api",
        "description": "Gin is a HTTP web framework written in Go (Golang). It features a Martini-like API with much better performance.",
        "stars_count": 78900, "forks_count": 8000, "open_issues_count": 210,
        "url": "https://github.com/gin-gonic/gin"
    },
    {
        "owner": "kubernetes", "name": "kubernetes", "full_name": "kubernetes/kubernetes",
        "language": "Go", "topics": "kubernetes,containers,devops,cloud-native,orchestration",
        "description": "Production-Grade Container Scheduling and Management.",
        "stars_count": 112000, "forks_count": 39500, "open_issues_count": 2800,
        "url": "https://github.com/kubernetes/kubernetes"
    },
    {
        "owner": "cli", "name": "cli", "full_name": "cli/cli",
        "language": "Go", "topics": "github,cli,go,golang,terminal,git",
        "description": "GitHub’s official command line tool.",
        "stars_count": 37200, "forks_count": 5500, "open_issues_count": 340,
        "url": "https://github.com/cli/cli"
    }
]

SEED_DEVELOPERS = [
    {
        "username": "alex_ml",
        "name": "Alex Chen",
        "avatar_url": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150&auto=format&fit=crop&q=80",
        "bio": "ML engineer & researcher. Deep learning enthusiast passionate about PyTorch, LLMs, transformer fine-tuning, and CUDA optimization.",
        "languages": "Python,C++",
        "repos_summary": "Active contributor to PyTorch vision models, transformers inference pipelines, scikit-learn metrics, and numpy tensor math.",
        "is_persona": True
    },
    {
        "username": "sarah_fullstack",
        "name": "Sarah Miller",
        "avatar_url": "https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=150&auto=format&fit=crop&q=80",
        "bio": "Full-stack web engineer building modern web applications with React, Next.js, TypeScript, Tailwind CSS, and Node.js microservices.",
        "languages": "TypeScript,JavaScript,Python",
        "repos_summary": "Author of open-source UI libraries, design systems with Radix UI, serverless Next.js dashboards, and Tailwind extensions.",
        "is_persona": True
    },
    {
        "username": "marcus_systems",
        "name": "Marcus Vance",
        "avatar_url": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&auto=format&fit=crop&q=80",
        "bio": "Systems programmer specialized in Rust, asynchronous runtimes with Tokio, memory safety, WebAssembly, and high-performance databases.",
        "languages": "Rust,C",
        "repos_summary": "Contributor to Tokio async IO, Polars SIMD kernels, Hyper HTTP protocol parsers, and Cargo plugin extensions.",
        "is_persona": True
    },
    {
        "username": "devon_backend",
        "name": "Devon Taylor",
        "avatar_url": "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=150&auto=format&fit=crop&q=80",
        "bio": "Backend and cloud engineer focusing on Go microservices, Kubernetes operators, Gin REST APIs, gRPC, and high-concurrency systems.",
        "languages": "Go,Python",
        "repos_summary": "Built cloud-native observability tooling, Kubernetes custom controllers, GitHub CLI extensions, and Gin middleware.",
        "is_persona": True
    },
    {
        "username": "elena_newbie",
        "name": "Elena Rostova (Cold Start)",
        "avatar_url": "https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=150&auto=format&fit=crop&q=80",
        "bio": "CS student starting out in open source! Learning Python and web development. Excited to pick up good first issues and write docs.",
        "languages": "Python",
        "repos_summary": "Beginner programmer, completed coursework in Python algorithms and Flask basics. No past repo contributions.",
        "is_persona": True
    },
    {
        "username": "liam_data",
        "name": "Liam Scott",
        "avatar_url": "https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?w=150&auto=format&fit=crop&q=80",
        "bio": "Data engineer and quantitative analyst. Big data processing with Polars, Pandas, SQL databases, and automated pipelines.",
        "languages": "Python,Rust,SQL",
        "repos_summary": "Built streaming pipelines, Polars lazy dataframe plugins, parquet benchmark tools, and SQLAlchemy schemas.",
        "is_persona": True
    }
]

SEED_ISSUES_TEMPLATES = [
    # FastAPI
    {
        "repo_slug": "tiangolo/fastapi",
        "title": "Add support for Annotated union types in query parameters validation",
        "body": "When using typing.Annotated with Union[int, str] in query parameters, OpenAPI schema generation fails to infer the correct anyOf schema. Expected behaviour is for Swagger UI to render valid parameter options.",
        "labels": "enhancement,pydantic,good first issue",
        "comments": 4, "is_beginner": True, "age_days": 5
    },
    {
        "repo_slug": "tiangolo/fastapi",
        "title": "Fix memory leak during streaming responses in async generator dependencies",
        "body": "Under high concurrency (1000+ req/s), using StreamingResponse with an async generator dependency causes connection tasks to linger in the event loop without garbage collection.",
        "labels": "bug,asyncio,high-priority",
        "comments": 12, "is_beginner": False, "age_days": 18
    },
    {
        "repo_slug": "tiangolo/fastapi",
        "title": "Documentation: Add complete tutorial for WebSocket authentication with JWT tokens",
        "body": "The current WebSocket docs only showcase basic query token passing. We should add a step-by-step example verifying JWT tokens during handshake and handling disconnection error codes.",
        "labels": "documentation,good first issue,help wanted",
        "comments": 2, "is_beginner": True, "age_days": 11
    },
    # PyTorch
    {
        "repo_slug": "pytorch/pytorch",
        "title": "Implement torch.compile support for custom quantized Linear layer operations",
        "body": "Running torch.compile(model) on 8-bit quantized linear layers fails Dynamo graph capture with unbacked SymInt symbol errors. We need to implement proper FakeTensor dispatch rules.",
        "labels": "module: dynamo,compiler,quantization",
        "comments": 8, "is_beginner": False, "age_days": 14
    },
    {
        "repo_slug": "pytorch/pytorch",
        "title": "Fix docstring typo and add code snippet in torch.nn.functional.scaled_dot_product_attention",
        "body": "The parameter description for attn_mask has a minor grammatical error, and there is no runnable example demonstrating the is_causal=True flag for autoregressive decoders.",
        "labels": "documentation,good first issue,starter",
        "comments": 1, "is_beginner": True, "age_days": 3
    },
    # Transformers
    {
        "repo_slug": "huggingface/transformers",
        "title": "Add flash-attention-2 support to Llama-3 modeling and kv-cache",
        "body": "Currently Llama3 models default to eager attention when run on RTX 4090 GPUs. Adding flash-attention-2 dispatch will reduce memory footprint by 40% on long sequence context (8k tokens).",
        "labels": "model: llama,optimization,help wanted",
        "comments": 15, "is_beginner": False, "age_days": 22
    },
    {
        "repo_slug": "huggingface/transformers",
        "title": "Beginner: Add test cases for tokenizer chat template formatting on special tokens",
        "body": "We need additional unit tests in tests/test_tokenization_utils.py checking that <|eot_id|> and <|start_header_id|> tokens are not stripped during apply_chat_template.",
        "labels": "tests,good first issue,nlp",
        "comments": 3, "is_beginner": True, "age_days": 7
    },
    # Scikit-Learn
    {
        "repo_slug": "scikit-learn/scikit-learn",
        "title": "Add support for sample_weight in HistGradientBoostingClassifier metrics evaluation",
        "body": "HistGradientBoostingClassifier does not propagate sample weights into early stopping validation loss calculations, causing skewed early stopping when dealing with imbalanced datasets.",
        "labels": "bug,module: ensemble,statistics",
        "comments": 6, "is_beginner": False, "age_days": 25
    },
    {
        "repo_slug": "scikit-learn/scikit-learn",
        "title": "Add beginner example script comparing PCA vs t-SNE on high-dimensional text datasets",
        "body": "Create a clean gallery example under examples/decomposition/ demonstrating dimensional reduction on the 20 newsgroups dataset with clear matplotlib scatter plots and explanations.",
        "labels": "documentation,examples,good first issue",
        "comments": 2, "is_beginner": True, "age_days": 9
    },
    # React
    {
        "repo_slug": "facebook/react",
        "title": "Fix hydration error mismatch warning on Server Action form reset",
        "body": "When a Server Action completes and invokes form.reset() during client rehydration, React logs a false positive hydration mismatch error in strict development mode.",
        "labels": "Component: Server Actions,bug,react-dom",
        "comments": 19, "is_beginner": False, "age_days": 16
    },
    {
        "repo_slug": "facebook/react",
        "title": "Improve TypeScript type inference for useActionState hook pending status",
        "body": "In @types/react, useActionState return tuple currently marks isPending as boolean | undefined rather than strictly boolean, requiring unnecessary type assertions.",
        "labels": "TypeScript,types,good first issue",
        "comments": 5, "is_beginner": True, "age_days": 6
    },
    # Next.js
    {
        "repo_slug": "vercel/next.js",
        "title": "Turbopack fails to resolve relative CSS modules imported in app/ router layouts",
        "body": "When running next dev --turbo with nested layout components importing .module.css via relative aliases, Turbopack throws an unhandled asset resolution error.",
        "labels": "area: Turbopack,bug,css",
        "comments": 14, "is_beginner": False, "age_days": 12
    },
    {
        "repo_slug": "vercel/next.js",
        "title": "Add good first issue: update example template for Tailwind CSS v4 integration",
        "body": "The examples/with-tailwindcss directory uses old tailwind.config.js format. Update the template to follow the new @import 'tailwindcss' configuration with clean TypeScript boilerplate.",
        "labels": "examples,good first issue,tailwind",
        "comments": 4, "is_beginner": True, "age_days": 4
    },
    # Tailwind CSS & UI
    {
        "repo_slug": "tailwindlabs/tailwindcss",
        "title": "Add color-mix utility support for CSS variables opacity modifiers",
        "body": "Allow dynamic opacity syntax like bg-primary/20 to compile down to modern CSS color-mix(in srgb, var(--primary) 20%, transparent) for theme variables without hex conversion.",
        "labels": "feature,css,compiler",
        "comments": 11, "is_beginner": False, "age_days": 20
    },
    {
        "repo_slug": "shadcn-ui/ui",
        "title": "Add accessibility keyboard navigation (arrow keys & home/end) to Carousel component",
        "body": "Ensure the Radix-based Carousel component supports arrow key navigation and focuses proper slide dots when voice-over or screen readers are activated.",
        "labels": "accessibility,good first issue,component: carousel",
        "comments": 3, "is_beginner": True, "age_days": 8
    },
    # Tokio & Rust
    {
        "repo_slug": "tokio-rs/tokio",
        "title": "Optimize task queue work-stealing algorithm under uneven worker thread workloads",
        "body": "In tokio multithreaded runtime, when one worker thread is saturated with compute tasks while others are idle, the work-stealing backoff loop causes excessive atomic CAS operations.",
        "labels": "C-enhancement,A-runtime,performance",
        "comments": 17, "is_beginner": False, "age_days": 30
    },
    {
        "repo_slug": "tokio-rs/tokio",
        "title": "Clarify error propagation and cancellation safety in tokio::select! macro docs",
        "body": "Add code examples to select! documentation demonstrating how dropping a pending future affects buffered socket reads and explaining the best patterns for cancellation safety.",
        "labels": "E-easy,good first issue,A-docs",
        "comments": 2, "is_beginner": True, "age_days": 10
    },
    {
        "repo_slug": "rust-lang/cargo",
        "title": "Fix cargo check panic when workspace member has circular dev-dependency with features",
        "body": "When a workspace package depends on another member as dev-dependency with specific feature flags, cargo resolver encounters a recursion depth limit panic during graph resolution.",
        "labels": "Command-check,Bug,Resolver",
        "comments": 9, "is_beginner": False, "age_days": 21
    },
    # Polars
    {
        "repo_slug": "pola-rs/polars",
        "title": "Implement SIMD-accelerated string contains with regex patterns in PyPolars",
        "body": "String search queries over large column chunks currently fall back to scalar regex matching. Using hyperscan or portable SIMD can accelerate string contains queries up to 4x.",
        "labels": "performance,rust,python-engine",
        "comments": 13, "is_beginner": False, "age_days": 19
    },
    {
        "repo_slug": "pola-rs/polars",
        "title": "Good first issue: Add docstring examples for pl.DataFrame.with_columns expression chaining",
        "body": "Improve user onboarding by providing clear docstrings and doctests demonstrating how to chain multiple pl.col() operations inside with_columns without temporary variables.",
        "labels": "good first issue,documentation,python",
        "comments": 1, "is_beginner": True, "age_days": 2
    },
    # Go / Gin / Kubernetes
    {
        "repo_slug": "gin-gonic/gin",
        "title": "Add Context.BindQueryHeader utility for uniform API request binding",
        "body": "Provide a helper function that decodes custom X-Api headers alongside query parameters directly into tagged struct models using standard Go reflect validators.",
        "labels": "enhancement,good first issue,api",
        "comments": 4, "is_beginner": True, "age_days": 6
    },
    {
        "repo_slug": "kubernetes/kubernetes",
        "title": "Kubelet pod eviction manager race condition during container runtime restarts",
        "body": "If containerd restarts while kubelet is evaluating ephemeral-storage limits, the pod status sync loop can misreport pod status as Failed before container state is recovered.",
        "labels": "sig/node,kind/bug,area/kubelet",
        "comments": 24, "is_beginner": False, "age_days": 35
    },
    {
        "repo_slug": "cli/cli",
        "title": "Add gh issue view --json comments,reactions formatting support",
        "body": "The gh issue view command currently does not support exporting emoji reactions and user author avatars when passed JSON filter flags. Add fields to GraphQL query payload.",
        "labels": "enhancement,good first issue,cli",
        "comments": 5, "is_beginner": True, "age_days": 9
    }
]

def seed_database(db: Session, force: bool = False) -> Dict[str, int]:
    """
    Populates database with high-quality, realistic seed data (repos, issues, developers, interactions).
    """
    existing_repos = db.query(Repository).count()
    if existing_repos > 0 and not force:
        logger.info("Database already seeded (%d repos found). Skipping seed.", existing_repos)
        return {
            "repos": existing_repos,
            "issues": db.query(Issue).count(),
            "developers": db.query(Developer).count(),
            "interactions": db.query(Interaction).count()
        }

    logger.info("Seeding database with repositories, developers, issues, and interactions...")

    # 1. Insert Repositories
    repo_map = {}
    for r_data in SEED_REPOSITORIES:
        repo = Repository(
            owner=r_data["owner"],
            name=r_data["name"],
            full_name=r_data["full_name"],
            language=r_data["language"],
            topics=r_data["topics"],
            description=r_data["description"],
            stars_count=r_data["stars_count"],
            forks_count=r_data["forks_count"],
            open_issues_count=r_data["open_issues_count"],
            url=r_data["url"],
            created_at=datetime.utcnow() - timedelta(days=random.randint(100, 1000))
        )
        db.add(repo)
        db.flush()
        repo_map[repo.full_name] = repo

    # 2. Insert Developers
    dev_map = {}
    for d_data in SEED_DEVELOPERS:
        dev = Developer(
            username=d_data["username"],
            name=d_data["name"],
            avatar_url=d_data["avatar_url"],
            bio=d_data["bio"],
            languages=d_data["languages"],
            repos_summary=d_data["repos_summary"],
            is_persona=d_data["is_persona"],
            created_at=datetime.utcnow() - timedelta(days=random.randint(50, 400))
        )
        db.add(dev)
        db.flush()
        dev_map[dev.username] = dev

    # 3. Insert Issues
    created_issues = []
    issue_number_counter = 101

    for template in SEED_ISSUES_TEMPLATES:
        repo = repo_map.get(template["repo_slug"])
        if not repo:
            continue

        issue = Issue(
            repo_id=repo.id,
            number=issue_number_counter,
            title=template["title"],
            body=template["body"],
            state="open",
            labels=template["labels"],
            comments_count=template["comments"],
            is_beginner_friendly=template["is_beginner"],
            created_at=datetime.utcnow() - timedelta(days=template["age_days"]),
            html_url=f"{repo.url}/issues/{issue_number_counter}"
        )
        issue_number_counter += 1
        db.add(issue)
        db.flush()
        created_issues.append((issue, template))

    # Add extra generated issues to reach 60+ realistic issues
    categories = [
        ("Python", "tiangolo/fastapi", ["pydantic", "asyncio", "openapi", "security", "router"]),
        ("Python", "pytorch/pytorch", ["cuda", "distributed", "autograd", "onnx", "mps"]),
        ("Python", "huggingface/transformers", ["tokenizer", "generation", "pipeline", "quantization"]),
        ("TypeScript", "facebook/react", ["compiler", "hooks", "devtools", "suspense"]),
        ("TypeScript", "vercel/next.js", ["routing", "caching", "server-components", "middleware"]),
        ("TypeScript", "tailwindlabs/tailwindcss", ["jit", "dark-mode", "grid", "variants"]),
        ("Rust", "tokio-rs/tokio", ["channel", "time", "sync", "fs", "signal"]),
        ("Rust", "pola-rs/polars", ["parquet", "lazy", "join", "groupby", "arrow"]),
        ("Go", "gin-gonic/gin", ["logger", "recovery", "render", "validator"]),
        ("Go", "kubernetes/kubernetes", ["apiserver", "etcd", "scheduler", "cni"])
    ]

    for cat_lang, repo_slug, subtopics in categories:
        repo = repo_map.get(repo_slug)
        if not repo:
            continue
        for sub in subtopics:
            is_beg = random.choice([True, False])
            age = random.randint(1, 45)
            labels = f"{sub},{'good first issue,starter' if is_beg else 'bug,enhancement'}"
            title = f"{'Beginner: ' if is_beg else 'Improve '}Refactor {sub} module and add unit tests"
            body = f"Enhance error handling, documentation, and boundary edge cases for {sub} in {repo.name}. Ensure full CI test coverage."
            
            issue = Issue(
                repo_id=repo.id,
                number=issue_number_counter,
                title=title,
                body=body,
                state="open",
                labels=labels,
                comments_count=random.randint(0, 10),
                is_beginner_friendly=is_beg,
                created_at=datetime.utcnow() - timedelta(days=age),
                html_url=f"{repo.url}/issues/{issue_number_counter}"
            )
            issue_number_counter += 1
            db.add(issue)
            db.flush()
            created_issues.append((issue, {"repo_slug": repo_slug, "is_beginner": is_beg}))

    # 4. Generate Implicit Developer-Issue Interactions (Stars, Comments, Commits, PRs)
    # Persona affinity logic:
    # alex_ml -> Python, PyTorch, Transformers, Scikit-learn
    # sarah_fullstack -> TypeScript, React, Next.js, Tailwind, Shadcn
    # marcus_systems -> Rust, Tokio, Cargo, Polars
    # devon_backend -> Go, Gin, Kubernetes, CLI
    # liam_data -> Python, Polars, Scikit-learn
    # elena_newbie -> Has ONLY 1 interaction (to test Cold-Start logic!)
    affinity = {
        "alex_ml": ["Python", "PyTorch", "transformers", "scikit-learn"],
        "sarah_fullstack": ["TypeScript", "react", "next.js", "tailwindcss", "ui"],
        "marcus_systems": ["Rust", "tokio", "cargo", "hyper", "polars"],
        "devon_backend": ["Go", "gin", "kubernetes", "cli"],
        "liam_data": ["Python", "Rust", "polars", "scikit-learn"]
    }

    interaction_types = [
        ("star", 1.0),
        ("comment", 2.5),
        ("commit", 4.0),
        ("pr_merge", 5.0)
    ]

    now = datetime.utcnow()
    total_interactions = 0

    for dev_username, keywords in affinity.items():
        dev = dev_map.get(dev_username)
        if not dev:
            continue

        for issue, meta in created_issues:
            repo = issue.repository
            text_bundle = f"{repo.language} {repo.full_name} {repo.topics} {issue.title} {issue.labels}".lower()
            
            # Check match probability
            matches = any(k.lower() in text_bundle for k in keywords)
            prob = 0.55 if matches else 0.05

            if random.random() < prob:
                itype, weight = random.choice(interaction_types)
                # Assign dates in the past (some older, some newer for holdout split)
                interaction_date = issue.created_at + timedelta(days=random.randint(0, 5))
                if interaction_date > now:
                    interaction_date = now

                inter = Interaction(
                    developer_id=dev.id,
                    issue_id=issue.id,
                    interaction_type=itype,
                    weight=weight,
                    created_at=interaction_date
                )
                db.add(inter)
                total_interactions += 1

    # Elena (Cold-Start Developer): Exactly 1 interaction on a Python good-first-issue
    elena = dev_map.get("elena_newbie")
    if elena:
        first_python_easy = db.query(Issue).join(Repository).filter(
            Repository.language == "Python",
            Issue.is_beginner_friendly == True
        ).first()
        if first_python_easy:
            db.add(Interaction(
                developer_id=elena.id,
                issue_id=first_python_easy.id,
                interaction_type="star",
                weight=1.0,
                created_at=now - timedelta(days=1)
            ))
            total_interactions += 1

    db.commit()
    logger.info("Database seeding successfully finished! Inserted %d repos, %d issues, %d devs, %d interactions.",
                len(repo_map), len(created_issues), len(dev_map), total_interactions)

    return {
        "repos": len(repo_map),
        "issues": len(created_issues),
        "developers": len(dev_map),
        "interactions": total_interactions
    }

def fetch_github_user_profile(username: str) -> Optional[Dict[str, Any]]:
    """
    Fetches real public GitHub profile and repository metadata using GitHub REST API.
    """
    headers = {"Accept": "application/vnd.github.v3+json"}
    if settings.GITHUB_TOKEN:
        headers["Authorization"] = f"token {settings.GITHUB_TOKEN}"

    try:
        user_res = requests.get(f"https://api.github.com/users/{username}", headers=headers, timeout=5)
        if user_res.status_code != 200:
            return None
        user_data = user_res.json()

        # Fetch recent user repos to infer languages and skills
        repos_res = requests.get(
            f"https://api.github.com/users/{username}/repos?sort=updated&per_page=10",
            headers=headers,
            timeout=5
        )
        languages = set()
        topics = []
        if repos_res.status_code == 200:
            for r in repos_res.json():
                if r.get("language"):
                    languages.add(r["language"])
                if r.get("topics"):
                    topics.extend(r["topics"][:3])

        return {
            "github_id": user_data.get("id"),
            "username": user_data.get("login"),
            "name": user_data.get("name") or user_data.get("login"),
            "avatar_url": user_data.get("avatar_url"),
            "bio": user_data.get("bio") or "Open source enthusiast",
            "languages": ",".join(list(languages)[:5]),
            "repos_summary": f"Recent repositories: {', '.join([t for t in topics[:6]])}"
        }
    except Exception as e:
        logger.warning("Error fetching GitHub profile for %s: %s", username, e)
        return None
