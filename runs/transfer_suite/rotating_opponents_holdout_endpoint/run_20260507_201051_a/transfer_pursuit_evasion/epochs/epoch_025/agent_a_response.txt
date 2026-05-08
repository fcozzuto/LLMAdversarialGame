def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    role = (observation.get("self_role", "") or "").lower()
    is_pursuer = ("purs" in role) or ("chaser" in role) or ("chase" in role) or ("pursuer" in role)
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y): 
        return 0 <= x < w and 0 <= y < h

    def dist(a, b, x, y):
        dx = abs(x - a)
        dy = abs(y - b)
        return dx if dx > dy else dy

    def obs_adj(x, y):
        c = 0
        for ddx in (-1, 0, 1):
            for ddy in (-1, 0, 1):
                nx, ny = x + ddx, y + ddy
                if (nx, ny) in obs:
                    c += 1
        return c

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    best = None
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        d = dist(ox, oy, nx, ny)
        o = obs_adj(nx, ny)
        center = abs(nx - cx) + abs(ny - cy)
        # Pursuer: minimize distance; Evader: maximize distance.
        primary = d if is_pursuer else -d
        # Deterministic tie-breakers: fewer adjacent obstacles, then prefer center (pursuer), or edges (evader).
        if is_pursuer:
            key = (primary, o, center, dx, dy)
        else:
            key = (primary, o, -center, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best = (dx, dy)

    return [int(best[0]), int(best[1])] if best is not None else [0, 0]