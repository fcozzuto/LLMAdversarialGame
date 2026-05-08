def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    obstacles = observation.get("obstacles", []) or []
    oset = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            oset.add((int(p[0]), int(p[1])))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inside(x, y): return 0 <= x < w and 0 <= y < h
    def valid(x, y): return inside(x, y) and (x, y) not in oset
    def man(x1, y1, x2, y2): return abs(x1 - x2) + abs(y1 - y2)
    def mobility(x, y):
        c = 0
        for dx, dy in moves:
            if valid(x + dx, y + dy):
                c += 1
        return c
    def corner_penalty(x, y):
        return 2.0 * (min(x, w - 1 - x) == 0 and min(y, h - 1 - y) == 0)
    def obs_prox(x, y):
        m = 99
        for oxp, oyp in oset:
            d = abs(x - oxp) + abs(y - oyp)
            if d < m: m = d
        return 0.0 if m == 99 else (2.0 / (m + 1))
    role = (observation.get("self_role", "") or "").lower()
    pursuer = ("purs" in role) and ("evad" not in role)
    # If role is unclear, assume pursuer when assigned as default.
    if role == "" or ("purs" in role and "evad" in role): pursuer = True

    best = None
    best_move = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        dist = man(nx, ny, ox, oy)
        mob = mobility(nx, ny)
        cp = corner_penalty(nx, ny)
        op = obs_prox(nx, ny)
        if pursuer:
            # Chase with obstacle-aware tie-breaks.
            val = (-dist) + 0.05 * mob - 0.03 * op
        else:
            # Evasion: maximize distance and mobility, avoid corners and obstacles.
            val = (dist) + 0.12 * mob - 1.2 * cp - 0.10 * op
        if best is None or val > best or (val == best and (dx, dy) < best_move):
            best = val
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]