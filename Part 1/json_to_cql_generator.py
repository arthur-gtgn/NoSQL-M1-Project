import json

def get_nested(d, *keys):
    for key in keys:
        if d is None:
            return None
        d = d.get(key)
    return d

def escape(text):
    return text.replace("'", "''") if isinstance(text, str) else text

def cassandra_value(val):
    """Convert Python value to a safe CQL literal."""
    if val is None:
        return "null"
    if isinstance(val, str):
        return f"'{escape(val)}'"
    if isinstance(val, (int, float)):
        return str(val)
    if isinstance(val, (dict)):
        if len(val) == 1:
            return cassandra_value(list(val.values())[0])
        return f"'{escape(json.dumps(val, ensure_ascii=False))}'"
    if isinstance(val, list):
        # Convertir la liste en JSON string
        return f"'{escape(json.dumps(val, ensure_ascii=False))}'"
    return val

insert_statements = []

with open("cleaned-companies2.json", "r") as file:
    for line in file:
        if not line.strip():
            continue  # skip empty lines
        company = json.loads(line)

        insert = f"""
        INSERT INTO companies (
            permalink, name, category_code, description, homepage_url,
            founded_year, founded_month, founded_day,
            deadpooled_year, deadpooled_month, deadpooled_day,
            number_of_employees, email_address, phone_number,
            total_money_raised, overview, twitter_username,
            acquisition_price_amount, acquisition_acquired_year,
            acquisition_acquired_month, acquisition_acquired_day,
            acquisition_acquiring_company
        ) VALUES (
            {cassandra_value(company.get("permalink"))},
            {cassandra_value(company.get("name"))},
            {cassandra_value(company.get("category_code"))},
            {cassandra_value(company.get("description"))},
            {cassandra_value(company.get("homepage_url"))},
            {cassandra_value(company.get("founded_year"))},
            {cassandra_value(company.get("founded_month"))},
            {cassandra_value(company.get("founded_day"))},
            {cassandra_value(company.get("deadpooled_year"))},
            {cassandra_value(company.get("deadpooled_month"))},
            {cassandra_value(company.get("deadpooled_day"))},
            {cassandra_value(company.get("number_of_employees"))},
            {cassandra_value(company.get("email_address"))},
            {cassandra_value(company.get("phone_number"))},
            {cassandra_value(company.get("total_money_raised"))},
            {cassandra_value(company.get("overview"))},
            {cassandra_value(company.get("twitter_username"))},
            {cassandra_value((company.get("acquisition") or {}).get("price_amount"))},
            {cassandra_value((company.get("acquisition") or {}).get("acquired_year"))},
            {cassandra_value((company.get("acquisition") or {}).get("acquired_month"))},
            {cassandra_value((company.get("acquisition") or {}).get("acquired_day"))},
            {cassandra_value(get_nested(company.get("acquisition"), "acquiring_company", "name"))}
        );
        """.strip()

        insert_statements.append(insert)

with open("insert_companies.cql", "w") as out_file:
    out_file.write("\n\n".join(insert_statements))

print("✅ Script insert_companies.cql généré avec succès.")
