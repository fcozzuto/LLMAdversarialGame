def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    resources = [tuple(p) for p in observation.get("resources", [])]

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    valid = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            valid.append((dx, dy))
    if not valid:
        return [0, 0]

    if not resources:
        tx, ty = (sx + ox) // 2, (sy + oy) // 2
        best = None
        best_key = None
        for dx, dy in valid:
            nx, ny = sx + dx, sy + dy
            key = (abs(nx - tx) + abs(ny - ty), abs(nx - ox) + abs(ny - oy), dx, dy)
            if best_key is None or key < best_key:
                best_key, best = key, (dx, dy)
        return [best[0], best[1]]

    def best_resource_score(px, py):
        # Prefer resources where we are closer than opponent; also keep some slack to prevent contest flips.
        best_key = None
        for rx, ry in resources:
            if (px, py) == (rx, ry):
                key = (-10**6, 0, 0)
            else:
                sd = abs(px - rx) + abs(py - ry)
                od = abs(px - ox) + abs(py - oy)
                # Larger (sd-od) is bad, so sort ascending on (sd-od)
                # Secondary terms: smaller own distance, larger opponent distance, deterministic tie via coords.
                key = (sd - od, sd, -(od), rx, ry)
            if best_key is None or key < best_key:
                best_key = key
        return best_key

    best = (0, 0)
    best_key = None
    ti = observation.get("turn_index", 0)
    for dx, dy in valid:
        nx, ny = sx + dx, sy + dy
        # If opponent is adjacent and a resource move doesn't improve much, step to preserve distance.
        opp_adj = (abs(nx - ox) <= 1 and abs(ny - oy) <= 1)
        rkey = best_resource_score(nx, ny)
        # Deterministic micro-bias: alternate tie-breaking by turn_index parity.
        parity_bias = (ti + dx * 7 + dy * 11) % 2
        dist_opp = abs(nx - ox) + abs(ny - oy)
        key = (rkey[0], rkey[1], rkey[2], 0 if (not opp_adj) else 1, -dist_opp, parity_bias, dx, dy)
        if best_key is None or key < best_key:
            best_key, best = key, (dx, dy)

    return [best[0], best[1]]