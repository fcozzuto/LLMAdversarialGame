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

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    # Use Chebyshev distance since diagonal moves are allowed and capture radius is 0.
    def dist(x, y, a, b):
        dx = abs(x - a)
        dy = abs(y - b)
        return dx if dx > dy else dy

    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obs:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    # In addition to distance, bias away from obstacles by preferring fewer adjacent obstacle cells.
    def obs_adj(x, y):
        c = 0
        for ddx in (-1, 0, 1):
            for ddy in (-1, 0, 1):
                if ddx == 0 and ddy == 0:
                    continue
                if (x + ddx, y + ddy) in obs:
                    c += 1
        return c

    # Deterministic tie-break: fixed secondary ordering.
    best = None
    best_score = None
    for dx, dy, nx, ny in legal:
        d = dist(nx, ny, ox, oy)
        oa = obs_adj(nx, ny)
        if is_pursuer:
            score = (-d, oa, dx, dy)  # minimize distance; among ties, fewer adjacent obstacles; fixed tie order
        else:
            score = (d, -oa, dx, dy)  # maximize distance; among ties, more obstacle-adjacency avoidance
        if best_score is None or score > best_score:
            best_score = score
            best = (dx, dy)

    return [int(best[0]), int(best[1])]