from mcp.server.fastmcp import FastMCP
import requests
from bs4 import BeautifulSoup

# Create a FastMCP server
mcp = FastMCP("FetchServer")

@mcp.tool()
def fetch(url: str) -> str:
    """Fetches the content of a URL and returns a cleaned text version.
    
    Args:
        url: The URL to fetch.
    """
    try:
        response = requests.get(
            url,
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=15
        )
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Remove script and style elements
        for script_or_style in soup(["script", "style"]):
            script_or_style.decompose()
            
        # Get text
        text = soup.get_text(separator=" ")
        
        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = " ".join(chunk for chunk in chunks if chunk)
        
        return text[:10000] # Limit to 10k chars
    except Exception as e:
        return f"Error fetching {url}: {str(e)}"

if __name__ == "__main__":
    mcp.run()
