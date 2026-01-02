def filter_by_semantics(candidates, obs_display, unit):
    display = (obs_display or "").lower()

    filtered = []

    for c in candidates:
        name = c["long_common_name"].lower()
        component = c["component"].lower()
        system = c["system"].lower()

        # Rate-type observations
        if "rate" in display and unit in ["/min", "min-1"]:
            if "breath" in component or "respiratory" in system:
                filtered.append(c)

        # Add future generic patterns here
        # heart rate, glucose, temp, etc.

    return filtered or candidates