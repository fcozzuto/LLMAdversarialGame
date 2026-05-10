def choose_move(observation):
    w = observation.get("grid_width") or 8
    h = observation.get("grid_height") or 8
    try:
        w = int(w)
    except:
        w = 8
    try:
        h = int(h)
    except:
        h = 8

    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = (sp[0] or 0), (sp[1] or 0)
    ox, oy = (op[0] or 0), (op[1] or 0)

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def blocked(x, y):
        return (x, y) in obs

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    self_role = (observation.get("self_role") or "").lower()
    env = (observation.get("environment_name") or "").lower()
    pursuer = ("pursuer" in self_role) or ("pursuit" in self_role) or ("evader" not in self_role and "pursuit" in env)

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and not blocked(nx, ny):
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    best_move = legal[0]
    best_val = None

    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        d = man(nx, ny, ox, oy)
        dc = abs(nx - cx) + abs(ny - cy)
        val = (d, dc) if pursuer else (d, -dc)
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]