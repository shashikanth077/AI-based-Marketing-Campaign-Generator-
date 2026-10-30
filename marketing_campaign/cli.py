"""Command-line entry point: python -m marketing_campaign.cli --product-id P1011"""

import argparse
import sys

from marketing_campaign.data import DEFAULT_DB_PATH, PRODUCTS, create_database, normalize_product_id


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="AI-based Marketing Campaign Generator")
    parser.add_argument("--product-id", help="e.g. P1011 (prompted if omitted)")
    parser.add_argument("--db", default=str(DEFAULT_DB_PATH), help="path to products.db")
    parser.add_argument("--direct", action="store_true",
                        help="skip the agents: SQL lookup + one structured LLM call")
    parser.add_argument("--creative", action="store_true",
                        help="use a high-temperature LLM for the copy")
    parser.add_argument("--safety-check", action="store_true", help="moderate output with Llama Guard")
    parser.add_argument("--list", action="store_true", help="list product IDs and exit")
    parser.add_argument("--verbose", action="store_true", help="show agent Thought/Action traces")
    args = parser.parse_args(argv)

    create_database(args.db)
    if args.list:
        for p in PRODUCTS:
            print(f"{p['product_id']}  {p['product_name']}")
        return 0

    try:
        product_id = normalize_product_id(args.product_id or input("Enter Product ID (e.g., P1011): "))
    except ValueError as exc:
        print(exc, file=sys.stderr)
        return 2

    from marketing_campaign import agents
    from marketing_campaign.llm import DEFAULT_GUARD_MODEL, get_llm

    llm = get_llm(temperature=0)
    writer_llm = get_llm(temperature=1.0) if args.creative else llm

    if args.direct:
        campaign = agents.generate_campaign_direct(product_id, writer_llm, args.db)
        if campaign is None:
            print(f"No product found with ID {product_id}", file=sys.stderr)
            return 1
        output = campaign.to_markdown()
    else:
        sql_agent = agents.build_sql_agent(llm, args.db, verbose=args.verbose)
        campaign_agent = agents.build_campaign_agent(llm, tool_llm=writer_llm, verbose=args.verbose)
        output = agents.generate_campaign(product_id, sql_agent, campaign_agent)

    if args.safety_check and not agents.is_safe(output, get_llm(0, DEFAULT_GUARD_MODEL)):
        print("Generated content was flagged as unsafe and has been withheld.", file=sys.stderr)
        return 3

    print(output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
