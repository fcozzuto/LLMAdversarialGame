def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    ox, oy = observation["opponent_position"]

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def d(a, b, c, e):
        return max(abs(c - a), abs(e - b))  # Chebyshev (matches diagonal movement)

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        nx, ny = sx + dx, sy + dy
        return [dx, dy] if valid(nx, ny) else [0, 0]

    # Pick best resource to contest: maximize advantage (opp_d - self_d), then closer to self
    best_r = None
    best_score = -10**18
    for rx, ry in resources:
        sd = d(sx, sy, rx, ry)
        od = d(ox, oy, rx, ry)
        adv = od - sd
        score = adv * 100 - sd
        if score > best_score:
            best_score = score
            best_r = (rx, ry)

    tx, ty = best_r

    # Choose move that most improves contested progress toward target
    cur_sd = d(sx, sy, tx, ty)
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        nd = d(nx, ny, tx, ty)
        # Prefer getting closer fast; slight penalty for moving away from being safe vs opponent
        val = (cur_sd - nd) * 200 - nd
        # If move would accidentally increase advantage loss (i.e., give opponent relative lead), penalize a bit
        opp_nd = d(ox, oy, tx, ty)
        val -= max(0, opp_nd - (nd + 0)) * 2
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]