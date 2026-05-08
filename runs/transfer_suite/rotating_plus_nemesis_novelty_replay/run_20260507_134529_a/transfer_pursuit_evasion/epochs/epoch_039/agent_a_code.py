def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0)) or (0, 0)
    ox, oy = observation.get("opponent_position", (0, 0)) or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    self_role = (observation.get("self_role") or "").lower()
    opponent_role = (observation.get("opponent_role") or "").lower()
    is_evader = ("evader" in self_role) or ("evader" in opponent_role and "pursuer" not in self_role)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist2(x, y, a, b):
        dx, dy = x - a, y - b
        return dx * dx + dy * dy

    def mobility(x, y):
        m = 0
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if ok(nx, ny):
                m += 1
        return m

    # Deterministic tie-break: fixed move order, then corner preference, then coordinate
    if is_evader:
        target = max(corners, key=lambda c: dist2(c[0], c[1], ox, oy))
    else:
        target = (ox, oy)

    best_move = [0, 0]
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        mob = mobility(nx, ny)
        if is_evader:
            # Prefer moving away from pursuer; bias toward farthest corner.
            s = dist2(nx, ny, ox, oy) + 0.25 * mob
            s += 0.01 * dist2(nx, ny, target[0], target[1])
        else:
            # Prefer closing distance; break ties by mobility (avoid being boxed in).
            s = -dist2(nx, ny, ox, oy) + 0.05 * mob
            s += 0.01 * (dist2(nx, ny, target[0], target[1]) == 0)
        if best_score is None or s > best_score:
            best_score = s
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]