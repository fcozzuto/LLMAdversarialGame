def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obs_list = observation.get("obstacles") or []
    obstacles = set((p[0], p[1]) for p in obs_list if len(p) >= 2)
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h
    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)
    selfT = set((p[0], p[1]) for p in (observation.get("self_territory") or []) if len(p) >= 2)
    oppT = set((p[0], p[1]) for p in (observation.get("opponent_territory") or []) if len(p) >= 2)
    candidates = []
    for k in ("unclaimed_cells", "unclaimed"):
        v = observation.get(k) or []
        if v:
            candidates = [(p[0], p[1]) for p in v if len(p) >= 2]
            break
    if not candidates:
        res = observation.get("resources") or []
        if res:
            candidates = [(p[0], p[1]) for p in res if len(p) >= 2]
    if not candidates:
        candidates = [(sx + dx, sy + dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if not (dx == 0 and dy == 0)]
        candidates = [c for c in candidates if inb(c[0], c[1]) and c not in obstacles]
        if not candidates:
            return [0, 0]
    opp_bias = 1
    if observation.get("scores") is not None:
        s = observation["scores"]
        my = s.get("self", 0) if isinstance(s, dict) else 0
        op = s.get("opponent", 0) if isinstance(s, dict) else 0
        if op > my:
            opp_bias = 1.6
    def cell_score(x, y):
        if (x, y) in obstacles:
            return -10**9
        dS = man(x, y, sx, sy)
        dO = man(x, y, ox, oy)
        edge = min(x, y, w - 1 - x, h - 1 - y)
        edge_bonus = (7 - edge)
        near_opp = 0
        for nx in (x - 1, x, x + 1):
            for ny in (y - 1, y, y + 1):
                if (nx, ny) != (x, y) and (nx, ny) == (ox, oy):
                    near_opp = 1
        front = 0
        if (x, y) in selfT:
            front = 1
        if (x, y) in oppT:
            front -= 2
        return (-2.0 * dS) + (1.2 * opp_bias * dO) + (0.7 * edge_bonus) + (5.0 * near_opp) + (4.0 * front)
    best = None
    best_sc = -10**18
    idx0 = (sx * 1315423911 + sy * 2654435761) & 1023
    for i, (x, y) in enumerate(candidates):
        if not inb(x, y) or (x, y) in obstacles:
            continue
        sc = cell_score(x, y) + ((i + idx0) % 2) * 0.001
        if sc > best_sc:
            best_sc = sc
            best = (x, y)
    if best is None:
        return [0, 0]
    tx, ty = best
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)
    move_order = [(dx, dy), (dx, 0), (0, dy), (dx, -dy), (-dx, dy), (0, 0)]
    for mx, my in move_order:
        nx, ny = sx + mx, sy + my
        if inb(nx, ny) and (nx, ny) not in obstacles:
            return [int(mx), int(my)]
    for mx in (-1, 0, 1):
        for my in (-1, 0, 1):
            if mx == 0 and my == 0:
                continue
            nx, ny = sx + mx, sy + my
            if inb(nx, ny) and (nx, ny