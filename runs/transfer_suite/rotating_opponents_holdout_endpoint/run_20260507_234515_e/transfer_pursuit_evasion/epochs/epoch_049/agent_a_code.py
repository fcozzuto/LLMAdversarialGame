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
    def corner_pen(x, y):
        return (1 if min(x, w - 1 - x) == 0 else 0) * (1 if min(y, h - 1 - y) == 0 else 0)
    def obs_prox(x, y):
        best = 10**9
        for ax, ay in oset:
            d = abs(x - ax) + abs(y - ay)
            if d < best: best = d
        return 0.0 if best == 10**9 else 1.0 / (best + 1)

    role = (observation.get("self_role", "") or "").lower()
    pursuer = ("purs" in role) and ("evad" not in role)
    # If role unclear, assume pursuer.
    if not role: pursuer = True

    best = None
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            score = -10**12
        else:
            d = abs(nx - ox) + abs(ny - oy)
            if pursuer:
                # Chase while avoiding dead-ends/corners and tight obstacle proximity.
                score = (-d * 10.0) + (2.0 * obs_prox(nx, ny)) - (corner_pen(nx, ny) * 3.0)
                # Prefer moves that keep options open.
                mob = 0
                for mx, my in moves:
                    tx, ty = nx + mx, ny + my
                    if valid(tx, ty): mob += 1
                score += mob * 0.4
            else:
                # Evade by increasing distance, and avoid corners/obstacles.
                score = (d * 10.0) - (corner_pen(nx, ny) * 6.0) - (obs_prox(nx, ny) * 3.0)
                mob = 0
                for mx, my in moves:
                    tx, ty = nx + mx, ny + my
                    if valid(tx, ty): mob += 1
                score += mob * 0.25
        if score > best_score:
            best_score = score
            best = [dx, dy]
    return [int(best[0]), int(best[1])]