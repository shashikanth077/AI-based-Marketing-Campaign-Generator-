"""Pydantic schema for structured campaign output."""

from pydantic import BaseModel, Field


class CampaignAssets(BaseModel):
    """The three campaign assets the generator must produce."""

    title: str = Field(description="Short, catchy, memorable marketing tagline (max ~10 words)")
    email_subject: str = Field(description="Subject line for the promotional email")
    email_body: str = Field(description="Professional, polite, engaging email of 100-150 words")
    cta: str = Field(description="Persuasive call-to-action telling the reader what to do next")

    def to_markdown(self) -> str:
        return (
            f"**Marketing Title:** {self.title}\n\n"
            f"**Email Draft:**\nSubject: {self.email_subject}\n\n{self.email_body}\n\n"
            f"**Call-to-Action (CTA):** {self.cta}"
        )
