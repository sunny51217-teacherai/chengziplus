"""Prompt engineering for teaching poster image generation.

Converts teaching topic + grade + style into optimized prompts
for image generation APIs.
"""

STYLE_TEMPLATES = {
    "cartoon": (
        "A bright, cheerful cartoon-style educational poster about {topic}. "
        "Designed for {grade} students. Features cute illustrated characters, "
        "rounded shapes, pastel and vibrant colors, large friendly typography, "
        "fun visual metaphors, and clear labeled diagrams. "
        "The layout is clean with a clear visual hierarchy. "
        "Kid-friendly and engaging. High quality illustration, 4K resolution."
    ),
    "minimal": (
        "A clean, minimalist educational poster about {topic}. "
        "Designed for {grade} students. Features a white background, "
        "elegant sans-serif typography, subtle color accents, "
        "simple geometric icons, plenty of white space, "
        "and a clear information hierarchy. "
        "Modern flat design aesthetic. Professional and readable. "
        "High quality graphic design, 4K resolution."
    ),
    "academic": (
        "A professional academic educational poster about {topic}. "
        "Designed for {grade} students. Features a structured grid layout, "
        "scientific diagrams and charts, serif typography for headings, "
        "a muted color palette with accent colors for key concepts, "
        "numbered sections, references area, and clear data visualizations. "
        "Formal academic style. High quality, print-ready, 4K resolution."
    ),
    "vibrant": (
        "A colorful, eye-catching educational poster about {topic}. "
        "Designed for {grade} students. Features bold gradients, "
        "dynamic compositions, large expressive typography, "
        "vivid illustrations, infographic elements, "
        "icons and visual metaphors, engaging visual flow. "
        "Modern and energetic design. High quality illustration, 4K resolution."
    ),
}

# Grade-level Chinese-English mapping for better prompt quality
GRADE_LABELS = {
    "小学": "elementary school (ages 6-12)",
    "初中": "middle school (ages 12-15)",
    "高中": "high school (ages 15-18)",
    "大学": "college/university",
    "幼儿园": "kindergarten (ages 3-6)",
}


def build_poster_prompt(topic: str, grade: str, style: str) -> str:
    """Build an optimized image generation prompt for a teaching poster.

    Args:
        topic: The teaching subject/topic (Chinese or English).
        grade: Target audience / grade level.
        style: Visual style - one of cartoon, minimal, academic, vibrant.

    Returns:
        A detailed English prompt optimized for image generation APIs.
    """
    template = STYLE_TEMPLATES.get(style)
    if template is None:
        available = ", ".join(STYLE_TEMPLATES.keys())
        raise ValueError(f"Unknown style '{style}'. Available: {available}")

    # Normalize grade label
    grade_label = GRADE_LABELS.get(grade, grade)

    prompt = template.format(topic=topic, grade=grade_label)

    # Add universal quality boosters
    prompt += (
        " Educational content is accurate and clearly presented. "
        "No watermarks. No text errors. "
        "Suitable for classroom display."
    )

    return prompt
