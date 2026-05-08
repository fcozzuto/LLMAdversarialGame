def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    role = str(observation.get("self_role", "")).lower()
    pursuer = any(k in role for k in ("pursuer", "hunter", "chaser", "pursuit", "attacker"))
    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy
    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles
    def clamp(v, lo, hi):
        return lo if v < lo else hi if v > hi else v

    # Local move scoring (9-neighborhood), deterministic tie-break by score then fixed ordering.
    def neighbor_clearance(x, y):
        c = 0
        for dx, dy in deltas:
            nx, ny = x + dx, y + dy
            if valid(nx, ny): c += 1
        return c

    center_x, center_y = (w - 1) / 2.0, (h - 1) / 2.0
    best = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny): 
            continue
        d = cheb(nx, ny, ox, oy)
        # Walls/corners penalty to avoid getting stuck when opponent is evasion_corner
        edge_pen = (nx == 0) + (nx == w - 1) + (ny == 0) + (ny == h - 1)
        dist_center = cheb(nx, ny, center_x, center_y)
        clr = neighbor_clearance(nx, ny)
        if pursuer:
            # Capture has absolute priority; otherwise reduce distance with a bias to stay mobile and centered.
            score = (-1000000.0 if d == 0 else -d * 1200.0 - (clr * 10.0) - edge_pen * 40.0 - dist_center * 2.0)
        else:
            # Evade: increase distance, prefer mobile positions, and avoid edges; deterministic tie-break.
            score = (1000000.0 if d == 0 else d * 1200.0 + (clr * 8.0) - edge_pen * 60.0 - dist_center * 0.5)
        cand = (score, dx, dy)
        if best is None or cand > best:
            best = cand

    if best is None:
        return [0, 0]
    return [int(best[1]), int(best[2])]