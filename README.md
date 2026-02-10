# chengziplus

make teaching and learning easier.

## Teaching Poster Generator

A Claude Code Skill that generates educational posters by calling image generation APIs.

### Supported APIs

| Provider | Model | Best For |
|----------|-------|----------|
| OpenAI | DALL-E 3 | Highest quality, best prompt understanding |
| Stability AI | Stable Diffusion 3 | Good quality, cost-effective |
| Silicon Flow | Flux | Chinese-friendly, affordable |

### Quick Start

```bash
# 1. Copy and configure your API key
cp .env.example .env
# Edit .env and add your API key

# 2. Generate a poster
python3 src/generate_poster.py \
  --topic "光合作用 Photosynthesis" \
  --grade "初中" \
  --style vibrant \
  --api openai
```

### Usage with Claude Code Skill

When using Claude Code, simply ask:

```
帮我生成一张关于光合作用的教学海报
Create a teaching poster about the water cycle for 5th graders
```

### Options

| Flag | Description | Default |
|------|-------------|---------|
| `--topic` | Teaching topic (Chinese/English) | Required |
| `--grade` | Target audience (小学/初中/高中/大学) | 初中 |
| `--style` | Visual style (cartoon/minimal/academic/vibrant) | vibrant |
| `--api` | API provider (openai/stability/siliconflow) | openai |
| `--size` | Image dimensions | 1024x1024 |
| `--output` | Output directory | ./output |

### Project Structure

```
chengziplus/
├── .claude/skills/teaching-poster/SKILL.md  # Claude Code skill definition
├── src/
│   ├── generate_poster.py                   # Main entry point
│   ├── api/
│   │   ├── base.py                          # Abstract API client
│   │   ├── factory.py                       # Client factory
│   │   ├── openai_client.py                 # DALL-E 3 client
│   │   ├── stability_client.py              # Stable Diffusion 3 client
│   │   └── siliconflow_client.py            # Flux client
│   └── prompts/
│       └── poster_prompt.py                 # Teaching poster prompt templates
├── output/                                  # Generated images
├── .env.example                             # API key template
└── .gitignore
```
