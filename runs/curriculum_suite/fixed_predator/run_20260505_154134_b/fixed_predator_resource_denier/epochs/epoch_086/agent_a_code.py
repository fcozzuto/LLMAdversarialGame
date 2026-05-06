def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    cand = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    legal = []
    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obs:
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    if resources:
        best_val = None
        best_move = (0, 0)
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            # Prefer moves that reduce (our dist - opponent dist) to the nearest resource.
            # Deterministic tie-breaker by (value, dx, dy).
            cur_best = None
            for r in resources:
                if not r or len(r) < 2:
                    continue
                rx, ry = int(r[0]), int(r[1])
                our_d = cheb(nx, ny, rx, ry)
                opp_d = cheb(ox, oy, rx, ry)
                gap = our_d - opp_d
                if cur_best is None or gap < cur_best:
                    cur_best = gap
            val = cur_best if cur_best is not None else 10**9
            t = (val, dx, dy)
            if best_val is None or t < best_val:
                best_val = t
                best_move = (dx, dy)
        return [int(best_move[0]), int(best_move[1])]

    # No resources: move to reduce distance to opponent; if tied, prefer centered movement.
    tx, ty = ox, oy
    best = None
    best_move = (0, 0)
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        d = cheb(nx, ny, tx, ty)
        center_d = cheb(nx, ny, w // 2, h // 2)
        t = (d, center_d, dx, dy)
        if best is None or t < best:
            best = t
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]