def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    turn = observation.get("turn_index", 0)

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    if not resources:
        tx, ty = (w - 1, 0) if ((sx + sy + turn) % 2 == 0) else (0, h - 1)
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        return [dx, dy]

    best_r = resources[0]
    best_v = -10**18
    for rx, ry in resources:
        ds = man(sx, sy, rx, ry)
        do = man(ox, oy, rx, ry)
        share = (1 if rx == ox else 0) + (1 if ry == oy else 0)
        parity = 1 if ((rx + ry) % 2) == ((turn + sx + sy) % 2) else 0
        v = (do - ds) * 80 + share * 12 + parity * 3 - ds * 0.5
        if v > best_v:
            best_v = v
            best_r = (rx, ry)

    rx, ry = best_r

    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                candidates.append((dx, dy, nx, ny))
    if not candidates:
        return [0, 0]

    curd = man(sx, sy, rx, ry)
    best_m = candidates[0]
    best_s = -10**18
    for dx, dy, nx, ny in candidates:
        nd = man(nx, ny, rx, ry)
        progress = curd - nd
        block = -1 if (nx == ox and ny == oy) else 0
        avoid = 0
        for ax, ay in obstacles:
            if abs(nx - ax) <= 1 and abs(ny - ay) <= 1:
                avoid -= 0.5
        # If opponent is close in this move, prefer paths that reduce their advantage.
        opp_d_now = man(ox, oy, rx, ry)
        opp_d_after = man(ox, oy, nx, ny)
        opp_effect = (opp_d_now - opp_d_after) * 0.05
        s = progress * 100 + block * 5 + avoid * 8 + opp_effect
        if s > best_s:
            best_s = s
            best_m = (dx, dy)

    return [best_m[0], best_m[1]]