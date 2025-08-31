import httpx

class verifierClient:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.client = httpx.AsyncClient(base_url=self.base_url)

    async def verify_document(self, document_type: str, document_data: dict) -> dict:
        """
        Mock external verification call.
        In real life, connect to Aashar, GST, PAN, etc. APIs.
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/verify/{document_type}", 
                json=document_data
            )
            response.raise_for_status()
            return response.json()
