def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    role = (str(observation.get("self_role", "")) + " " + str(observation.get("opponent_role", ""))).lower()
    evading = any(k in role for k in ("evade", "runner", "flee", "evasion", "evader"))
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def cheb_dist(x, y): 
        dx = abs(ox - x); dy = abs(oy - y)
        return dx if dx > dy else dy

    def obst_pen(x, y):
        if (x, y) in obstacles: 
            return 10**6
        p = 0
        for ax, ay in obstacles:
            d = abs(ax - x) + abs(ay - y)
            if d == 0: return 10**6
            if d == 1: p += 30
            elif d == 2: p += 10
            elif d == 3: p += 4
        return p

    def edge_bonus(x, y):
        # Prefer hugging relevant edges deterministically to reduce zigzag freedom.
        # Pursuer: aim for edges near evader; Evader: aim for far edge.
        t = 0
        t += min(x, w - 1 - x)  # smaller near edges
        return -t if evading else t

    best = None
    best_sc = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d = cheb_dist(nx, ny)
        pen = obst_pen(nx, ny)
        # If evading, maximize distance; else minimize distance.
        sc = (-d if evading else d) - pen + edge_bonus(nx, ny)
        # Tie-break deterministically by fixed move order and then coordinates.
        if best is None or sc > best_sc or (sc == best_sc and (dx, dy) < best):
            best_sc = sc
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]