def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    t = observation.get("turn_index", 0)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    dirs = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]

    if not resources:
        best = (0, 0, -10**9)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            d_op = md((nx, ny), (ox, oy))
            score = d_op
            if score > best[2] or (score == best[2] and (dx, dy) < (best[0], best[1])):
                best = (dx, dy, score)
        return [best[0], best[1]]

    # Select target resource: prefer those where we are earlier than opponent, with deterministic alternation.
    parity = 1 if (t % 2 == 0) else -1
    best_r = None
    best_val = -10**9
    for rx, ry in resources:
        ds = abs(rx - sx) + abs(ry - sy)
        do = abs(rx - ox) + abs(ry - oy)
        # If parity is +1, favor earlier-by-opp distance; else slightly favor closer for aggressiveness.
        val = (do - ds) * parity - ds
        # Deterministic tie-break by coordinate sum then lexicographic
        if val > best_val or (val == best_val and ((rx + ry), rx, ry) < ((best_r[0] + best_r[1]), best_r[0], best_r[1])):
            best_val = val
            best_r = (rx, ry)

    tx, ty = best_r
    opp_dist = abs(tx - ox) + abs(ty - oy)

    # Choose move to reduce distance to target while keeping away from obstacles and optionally away from opponent.
    best = (0, 0, -10**9)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        new_d = abs(tx - nx) + abs(ty - ny)
        d_to_opp = abs(ox - nx) + abs(oy - ny)
        # Higher is better: closer to target, and if we're not already clearly winning the race, keep some distance.
        score = -new_d * 10 + d_to_opp
        if parity < 0 and opp_dist <= 6:
            score += (d_to_opp if d_to_opp > 0 else -100)
        if score > best[2] or (score == best[2] and (dx, dy) < (best[0], best[1])):
            best = (dx, dy, score)

    # Fallback: if all moves blocked, stay.
    return [best[0], best[1]]