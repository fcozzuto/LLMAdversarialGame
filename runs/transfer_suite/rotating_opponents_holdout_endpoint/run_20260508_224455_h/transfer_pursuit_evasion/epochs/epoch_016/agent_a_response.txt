def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    role = str(observation.get("self_role", "")).lower()
    opp_role = str(observation.get("opponent_role", "")).lower()
    evader_keys = ("evader", "evade", "escape", "runner", "evasion")
    we_evade = any(k in role for k in evader_keys) and not any(k in opp_role for k in evader_keys)

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def blocked(x, y): return (x, y) in obstacles

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    target_corner = max(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))

    def free_neighbors(x, y):
        cnt = 0
        for dx2, dy2 in moves:
            if dx2 == 0 and dy2 == 0: continue
            x2, y2 = x + dx2, y + dy2
            if inb(x2, y2) and not blocked(x2, y2):
                cnt += 1
        return cnt

    def eval_move(nx, ny):
        if not inb(nx, ny) or blocked(nx, ny):
            return -10**9
        d = abs(nx - ox) + abs(ny - oy)
        safety = free_neighbors(nx, ny)
        to_corner = abs(nx - target_corner[0]) + abs(ny - target_corner[1])
        if we_evade:
            return 10*d + 2*safety - 0.2*to_corner
        else:
            return -10*d + 2*safety - 0.2*to_corner

    best = None
    bestv = -10**18
    # Deterministic tie-break order: fixed moves list, then smallest distance to corner for evader / to opponent for pursuer
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        v = eval_move(nx, ny)
        if v > bestv:
            bestv = v
            best = [dx, dy]
    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]