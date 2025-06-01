import csv


class CsvWriter:
    FIELDS = [
        "Name",
        "Last Communication",
        "Phone",
        "Email",
        "Address",
        "Relationships",
        "Background",
        "Stage",
        "Source",
        "Agent",
        "Lender",
        "Price",
        "Timeframe",
        "Tags",
        "Ylopo Seller Report",
        "Testing Box",
    ]

    def write_people(self, people, output_path, append=False):
        mode = "a" if append else "w"
        with open(output_path, mode, newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=self.FIELDS)
            if not append:
                writer.writeheader()
            for person in people:
                row = self._person_to_row(person)
                writer.writerow(row)

    def _person_to_row(self, person):
        # Helper to get first primary or first item from a list of dicts
        def get_first(items, key="value"):
            if not items:
                return ""
            primary = next((item for item in items if item.get("isPrimary")), None)
            if primary:
                return primary.get(key, "")
            return items[0].get(key, "")

        # Address formatting
        def format_address(addresses):
            if not addresses:
                return ""
            addr = addresses[0]
            parts = [
                addr.get("street", ""),
                addr.get("city", ""),
                addr.get("state", ""),
                addr.get("code", ""),
                addr.get("country", ""),
            ]
            return ", ".join([p for p in parts if p])

        return {
            "Name": person.get("name", ""),
            "Last Communication": person.get("lastActivity", ""),
            "Phone": get_first(person.get("phones", [])),
            "Email": get_first(person.get("emails", [])),
            "Address": format_address(person.get("addresses", [])),
            "Relationships": "",  # Not available in API response
            "Background": "",  # Not available in API response
            "Stage": person.get("stage", ""),
            "Source": person.get("source", ""),
            "Agent": person.get("assignedTo", ""),
            "Lender": person.get("assignedLenderName", ""),
            "Price": person.get("price", ""),
            "Timeframe": person.get("timeframeStatus", ""),
            "Tags": ", ".join(person.get("tags", [])),
            "Ylopo Seller Report": "",  # Not available in API response
            "Testing Box": "",  # Not available in API response
        }
