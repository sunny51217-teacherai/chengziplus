---
name: teaching-poster
description: Generate teaching posters by calling image generation APIs. Supports DALL-E 3, Stability AI, and Silicon Flow.
---

# Teaching Poster Generation Skill

This skill generates visually appealing teaching posters by combining pedagogical prompt engineering with image generation APIs.

## Usage

When the user asks to create a teaching poster (教学海报), follow these steps:

1. **Clarify the topic**: Ask the user for the teaching subject, target audience (grade level), and any style preferences if not already provided.

2. **Generate the poster**: Run the poster generation script:
   ```bash
   python3 /home/user/chengziplus/src/generate_poster.py \
     --topic "<teaching topic>" \
     --grade "<target grade/audience>" \
     --style "<style: cartoon|minimal|academic|vibrant>" \
     --api "<api provider: openai|stability|siliconflow>" \
     --output "/home/user/chengziplus/output/"
   ```

3. **Report the result**: Tell the user where the generated image is saved, and show them the prompt that was used.

## Supported API Providers

| Provider | Model | Env Variable |
|----------|-------|-------------|
| OpenAI | DALL-E 3 | `OPENAI_API_KEY` |
| Stability AI | Stable Diffusion 3 | `STABILITY_API_KEY` |
| Silicon Flow | Flux | `SILICONFLOW_API_KEY` |

## Configuration

API keys should be set in `/home/user/chengziplus/.env` or as environment variables.

## Style Options

- `cartoon` - Bright, friendly cartoon style suitable for younger students (K-6)
- `minimal` - Clean, minimalist design with clear typography
- `academic` - Professional academic poster layout
- `vibrant` - Colorful, eye-catching design with bold graphics

## Examples

```
User: 帮我生成一张关于光合作用的教学海报
→ python3 src/generate_poster.py --topic "光合作用 Photosynthesis" --grade "初中" --style vibrant --api openai

User: Create a poster about fractions for 3rd graders
→ python3 src/generate_poster.py --topic "Fractions" --grade "3rd grade" --style cartoon --api openai
```
