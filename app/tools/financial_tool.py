from mcp import StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.client.session import ClientSession
import asyncio
import sys
import os

FINANCIAL_SOURCES = {
    "stocks": "https://finance.yahoo.com/markets/stocks/most-active/",
    "crypto": "https://finance.yahoo.com/markets/crypto/all/",
    "currencies": "https://finance.yahoo.com/markets/currencies/"
}

async def financial_data_tool(query: str) -> str:
    """Retrieves live stock, crypto, and currency data from Yahoo Finance.
    This tool routes requests through a specialized MCP fetch server.
    
    Args:
        query: The financial topic to search for (e.g., 'stocks', 'crypto', 'bitcoin', 'usd').
    """
    query_lower = query.lower()
    
    if any(word in query_lower for word in ["stock", "market", "nasdaq"]):
        category = "stocks"
    elif any(word in query_lower for word in ["crypto", "bitcoin", "ethereum", "btc", "eth"]):
        category = "crypto"
    else:
        category = "currencies"
        
    url = FINANCIAL_SOURCES[category]
    
    # Use the absolute path to the venv python and the mcp server
    python_exe = sys.executable
    mcp_script = os.path.abspath("mcp-server/main.py")
    
    server_params = StdioServerParameters(
        command=python_exe,
        args=[mcp_script],
    )
    
    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                # Call the 'fetch' tool on the MCP server
                result = await session.call_tool("fetch", arguments={"url": url})
                
                # result.content is a list of content blocks
                content_text = ""
                for block in result.content:
                    if hasattr(block, 'text'):
                        content_text += block.text
                    else:
                        content_text += str(block)
                        
                return f"Financial Data for {category} (Source: {url}):\n\n{content_text[:5000]}"
    except Exception as e:
        return f"Error connecting to MCP server: {str(e)}"

# For standalone testing
if __name__ == "__main__":
    res = asyncio.run(financial_data_tool("What are the top stocks?"))
    print(res)
