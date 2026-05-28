from mcp import StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.client.session import ClientSession
import asyncio
import sys
import os
from typing import Literal

FINANCIAL_SOURCES = {
    "stocks": "https://finance.yahoo.com/markets/stocks/most-active/",
    "crypto": "https://finance.yahoo.com/markets/crypto/all/",
    "currencies": "https://finance.yahoo.com/markets/currencies/"
}

async def financial_data_tool(
    category: Literal["stocks", "crypto", "currencies"]
) -> str:
    """Retrieves live financial data from Yahoo Finance via an MCP fetch server.
    
    Args:
        category: The category of financial data to retrieve. 
                  Must be one of 'stocks', 'crypto', or 'currencies'.
    """
    url = FINANCIAL_SOURCES.get(category)
    if not url:
        return f"Invalid category: {category}. Choose from stocks, crypto, or currencies."
        
    # Phase 3 Requirement: Use the Anthropic fetch reference implementation via Docker
    server_params = StdioServerParameters(
        command="docker",
        args=["run", "-i", "--rm", "mcp/fetch"],
    )
    
    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                # Call the 'fetch' tool on the MCP server
                result = await session.call_tool("fetch", arguments={"url": url})
                
                content_text = ""
                for block in result.content:
                    if hasattr(block, 'text'):
                        content_text += block.text
                    else:
                        content_text += str(block)
                        
                return f"Financial Data for {category} (Source: {url}):\n\n{content_text[:5000]}"
    except Exception as e:
        return f"Error connecting to MCP server: {str(e)}"
