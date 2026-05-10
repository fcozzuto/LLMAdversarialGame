def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    self_role = (observation.get("self_role", "") or "").lower()
    opp_role = (observation.get("opponent_role", "") or "").lower()
    self_pursuer = ("pursuer" in self_role) or ("pursue" in self_role) or ("chaser" in self_role)
    opp_pursuer = ("pursuer" in opp_role) or ("pursue" in opp_role) or ("chaser" in opp_role)
    pursuer = self_pursuer or (opp_pursuer and not self_pursuer)

    obstacles = observation.get("obstacles", []) or []
    obs = []
    for b in obstacles:
        if isinstance(b, (list, tuple)) and len(b) >= 2:
            obs.append((int(b[0]), int(b[1])))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist2(x, y, a, b):
        dx, dy = x - a, y - b
        return dx * dx + dy * dy

    def obstacle_pen(x, y):
        p = 0
        for bx, by in obs:
            dx = abs(x - bx)
            dy = abs(y - by)
            if dx == 0 and dy == 0:
                return 10**9
            d = dx if dx > dy else dy
            if d == 1:
                p += 7
            elif d == 2:
                p += 2
        return p

    best = None
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        op_pen = obstacle_pen(nx, ny)
        if op_pen >= 10**8:
            continue
        d2 = dist2(nx, ny, ox, oy)
        man = abs(nx - ox) + abs(ny - oy)
        # Pursuer: minimize distance; Evader: maximize distance.
        if pursuer:
            score = d2 - 0.15 * man + op_pen * 1.0
        else:
            score = -d2 + 0.10 * man + op_pen * 1.0
        # Deterministic tie-break: prefer smaller (dx,dy) lexicographically.
        if best is None or score < best_score or (score == best_score and (dx, dy) < best):
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]