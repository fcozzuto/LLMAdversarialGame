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
    self_is_evader = "evader" in self_role

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def mobility(x, y):
        m = 0
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if ok(nx, ny):
                m += 1
        return m

    # Distance metric: Chebyshev aligns with diagonal capture/approach
    def dist(x, y):
        return max(abs(x - ox), abs(y - oy))

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    target = None
    if self_is_evader:
        # Farthest corner from opponent (consistent wall-running bias)
        tx, ty = max(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))
        target = (tx, ty)
    else:
        target = (ox, oy)

    best = None
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        m = mobility(nx, ny)
        if self_is_evader:
            # Primary: maximize distance; secondary: drift toward far corner; tertiary: escape mobility
            d = dist(nx, ny)
            corner_d = abs(nx - target[0]) + abs(ny - target[1])
            # Higher score is better
            score = d * 1000 + m * 10 - corner_d
        else:
            # Primary: minimize distance; secondary: maximize mobility; tertiary: move toward opponent
            d = dist(nx, ny)
            opp_d = abs(nx - target[0]) + abs(ny - target[1])
            score = -d * 1000 + m * 10 - opp_d

        key = (score, -m, -dx, -dy)
        if best is None or key > best_score:
            best = (dx, dy)
            best_score = key

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]