"""
A sample module that turns two dicts with type
https://app.swaggerhub.com/apis-docs/xSke/PluralKit/1.1#/Systems/GetSystem and
https://app.swaggerhub.com/apis-docs/xSke/PluralKit/1.1#/Systems/GetSystemFronters
into {"details": string, "state": string}.
Must contain a fronters_to_string function.
"""


def fronters_to_string(system_info, fronters):
    members = fronters["members"]

    details = ", ".join(
        map(
            lambda member: member["display_name"]
            if member["display_name"] is not None
            else member["name"],
            members,
        )
        if len(members)
        else "(none)"
    )

    state = system_info["name"] if system_info["name"] is not None else "---"
    return {"details": details, "state": state}
