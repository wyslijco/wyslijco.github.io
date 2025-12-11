import re
import urllib


class ProductsAdapter:
    """
    Converts a string with a list of products into the list of dicts
    with product names and their links.

    When the link is missing, it adds a link to the search page for the
    product in the Allegro service.

    The input data string should be a list of products separated by newlines.
    Each line consists of a product name and an optional link to the product
    at the end of the line.
    """

    def __init__(self, data: str):
        self.data: str = data

    def _get_product_search_link(self, product_name: str) -> str:
        encoded_product = urllib.parse.quote(product_name)
        return f"https://allegro.pl/listing?string={encoded_product}"

    def _line_to_product_dict(self, line: str) -> dict[str, str]:
        f"""
        Converts a product line to the dict with the product name 
        and the link to the product.

        Example 1: Product with a link
        Input: Some product 1 https://domain.com
        Output:
        {
            "name": "Some product 1",
            "link": "https://domain.com"
        }

        Example 2: Product without a link
        Input: Some product 2
        Output:
        {
            "name": "Some product 2",
            "link": "https://allegro.pl/..."
        }
        """
        *name, link = line.split()

        # check if link is actually a link or just part of the product name
        if not re.match(r"^https?://", link):
            name.append(link)
            link = self._get_product_search_link(" ".join(name))

        return {
            "name": " ".join(name),
            "link": link,
        }

    @property
    def products(self) -> list[dict[str, str]]:
        return [
            self._line_to_product_dict(line.strip())
            for line in self.data.splitlines()
            if len(line.strip())
        ]
