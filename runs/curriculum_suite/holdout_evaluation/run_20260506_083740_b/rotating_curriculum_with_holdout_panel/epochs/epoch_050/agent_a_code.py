def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    ob = set()
    for p in obstacles:
        if p and len(p) >= 2:
            ob.add((int(p[0]), int(p[1])))

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in ob:
            legal.append((dx, dy))

    if not legal:
        return [0, 0]

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    # Edge-patrol response: bias toward the "far side" relative to the opponent (different niche from direct interception).
    tx_dir = 1 if ox < cx else -1
    ty_dir = 1 if oy < cy else -1

    def md(ax, ay, bx, by): return abs(ax - bx) + abs(ay - by)

    best_res = None
    best_key = None
    for r in resources:
        if not r or len(r) < 2:
            continue
        rx, ry = int(r[0]), int(r[1])
        if not inb(rx, ry) or (rx, ry) in ob:
            continue
        # Prefer resources on the far side; then maximize our advantage margin (opp_dist - our_dist).
        far_bias = -(tx_dir * rx + ty_dir * ry)
        our_d = md(sx, sy, rx, ry)
        opp_d = md(ox, oy, rx, ry)
        margin = opp_d - our_d
        key = (far_bias, -margin, our_d)
        if best_key is None or key < best_key:
            best_key, best_res = key, (rx, ry)

    rx, ry = best_res if best_res is not None else (sx, sy)

    # Choose the legal move that most reduces our distance to the chosen far-side target.
    # Tie-break by maximizing opponent distance (helps avoid race).
    best_move = (0, 0)
    best_val = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        our_d2 = md(nx, ny, rx, ry)
        opp_d2 = md(nx, ny, ox, oy)
        val = (our_d2, -opp_d2)
        if best_val is None or val < best_val:
            best_val, best_move = val, (dx, dy)

    return [int(best_move[0]), int(best_move[1])]