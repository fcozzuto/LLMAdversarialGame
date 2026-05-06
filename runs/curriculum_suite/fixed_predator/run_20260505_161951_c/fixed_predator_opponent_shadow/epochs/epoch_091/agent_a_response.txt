def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    resources = observation.get("resources", [])
    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

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
            d = man(nx, ny, tx, ty)
            k = (d, man(nx, ny, ox, oy))
            if best_key is None or k < best_key:
                best_key, best = k, (dx, dy)
        return [best[0], best[1]]

    # Pick a contested resource deterministically
    best_r = None
    best_r_key = None
    for rx, ry in resources:
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        # prefer resources where we are relatively closer; tie-break by self closeness
        k = (sd - 0.9 * od, sd, rx, ry)
        if best_r_key is None or k < best_r_key:
            best_r_key, best_r = k, (rx, ry)

    tx, ty = best_r
    cur_sd = man(sx, sy, tx, ty)

    # Move to reduce distance to target; if tie, prefer moves that increase distance from opponent
    best = (0, 0)
    best_key = None
    for dx, dy in valid:
        nx, ny = sx + dx, sy + dy
        nd = man(nx, ny, tx, ty)
        # compute opponent closeness relative to us at the target neighborhood
        opp_dist = man(nx, ny, ox, oy)
        k = (nd - cur_sd, nd, -opp_dist, dx, dy)
        if best_key is None or k < best_key:
            best_key, best = k, (dx, dy)

    return [int(best[0]), int(best[1])]