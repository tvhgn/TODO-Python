from textual.app import App, ComposeResult
from textual.widgets import Label

class TextDisplayer(App):
    """
    A simple app to display some text.
    """
    def compose(self) -> ComposeResult:
        yield Label("")
    
    def update_text(self, text: str):
        """Displays the text supplied."""
        self.query_one(Label).update(text)
        