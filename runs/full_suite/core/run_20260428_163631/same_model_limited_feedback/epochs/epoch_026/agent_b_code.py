def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b, c, d):
        dx = a - c
        dy = b - d
        return abs(dx) + abs(dy)

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    if not resources:
        best = (0, 0, -10**9, 0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            myd = dist(nx, ny, ox, oy)
            # Prefer staying closer to center-ish
            val = -myd
            if val > best[2]:
                best = (dx, dy, val, nx, ny)
        return [best[0], best[1]]

    # Pick resource that maximizes how much closer we are than opponent
    best_res = None
    best_lead = -10**18
    for rx, ry in resources:
        myd = dist(sx, sy, rx, ry)
        opd = dist(ox, oy, rx, ry)
        lead = opd - myd
        # Slight tie-breaker: prefer closer absolute distance
        val = (lead, -myd)
        if best_res is None or val > (best_lead, -dist(sx, sy, best_res[0], best_res[1])):
            best_res = (rx, ry)
            best_lead = lead

    tx, ty = best_res
    cur_myd = dist(sx, sy, tx, ty)

    # Choose move that improves our distance to target and/or keeps lead over opponent
    best = (0, 0, -10**18)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        myd = dist(nx, ny, tx, ty)
        opd = dist(ox, oy, tx, ty)
        lead = opd - myd
        # Reward getting closer; reward lead; penalize moving away
        val = 5 * (cur_myd - myd) + 3 * lead
        # Small preference for not changing direction too much
        val -= 0.1 * (abs(dx) + abs(dy))
        if val > best[2]:
            best = (dx, dy, val)
    # If all moves invalid, stay
    return [best[0], best[1]]