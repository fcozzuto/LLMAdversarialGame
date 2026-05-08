def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    cand = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny):
                cand.append((dx, dy, nx, ny))
    if not cand:
        return [0, 0]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    valid_resources = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if inb(x, y):
                valid_resources.append((x, y))
    if not valid_resources:
        # Fallback: maximize distance from opponent
        best = None
        for dx, dy, nx, ny in cand:
            val = (man(nx, ny, ox, oy), -man(nx, ny, sx, sy))
            if best is None or val > best[0]:
                best = (val, dx, dy)
        return [best[1], best[2]]

    best_move = None
    best_val = None
    for dx, dy, nx, ny in cand:
        # Choose the resource where we are most ahead (opponent farther than us).
        best_res_val = None
        for rx, ry in valid_resources:
            self_d = man(nx, ny, rx, ry)
            opp_d = man(ox, oy, rx, ry)
            # Encourage collecting quickly while keeping opponent behind; slight bias to closer resources.
            val = (opp_d - self_d, -self_d)
            if best_res_val is None or val > best_res_val:
                best_res_val = val
        # Also consider denying: move that increases our distance from opponent as secondary.
        deny = man(nx, ny, ox, oy) - man(sx, sy, ox, oy)
        total = (best_res_val[0], best_res_val[1], deny, -abs(dx) - abs(dy))
        if best_val is None or total > best_val:
            best_val = total
            best_move = (dx, dy)
    return [best_move[0], best_move[1]]