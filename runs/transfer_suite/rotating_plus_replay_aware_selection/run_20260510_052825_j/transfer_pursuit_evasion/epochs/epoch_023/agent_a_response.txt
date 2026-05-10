def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            try:
                obs.add((int(p[0]), int(p[1])))
            except:
                pass

    self_role = str(observation.get("self_role") or "").lower()
    opponent_role = str(observation.get("opponent_role") or "").lower()
    is_evader = ("evad" in self_role) or (self_role == "evader") or ("evader" in self_role)
    is_pursuer = ("purs" in self_role) or (self_role == "pursuer")
    if is_evader:
        mode = "evade"
    elif is_pursuer:
        mode = "pursue"
    else:
        mode = "pursue" if (("evad" in opponent_role) or (opponent_role == "evader")) else "evade"

    t = int(observation.get("turn_index", 0) or 0)
    prefs = 1 if (t % 2 == 0) else 0
    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    corner = corners[(t + (sx + 2 * sy)) % 4]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def free(x, y): return inb(x, y) and (x, y) not in obs
    dirs4 = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    def man(x1, y1, x2, y2):
        dx = x1 - x2; dy = y1 - y2
        return (dx * dx + dy * dy)  # squared

    best = None
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        d2 = man(nx, ny, ox, oy)
        edge = (nx == 0 or nx == w - 1 or ny == 0 or ny == h - 1)
        obst_adj = 0
        for ax, ay in dirs4:
            px, py = nx + ax, ny + ay
            if inb(px, py) and (px, py) in obs:
                obst_adj += 1
        toward_corner = man(nx, ny, corner[0], corner[1])
        if mode == "evade":
            # avoid getting boxed: prefer larger distance, edge when useful, and fewer obstacle-adjacent cells
            val = (d2 * 1000) + (1 if edge else 0) * 10 - obst_adj * 5 - toward_corner * (1 if prefs == 0 else 0.2)
        else:
            # pursue: minimize distance; also bias toward reducing ability of evader to slip by avoiding obstacle adjacency
            val = (-d2 * 1000) - (1 if edge else 0) * 3 + toward_corner * (0.2 if prefs == 1 else 0.0) - obst_adj * 4
        if best is None or val > best_val:
            best_val = val
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best