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
    def dist2(a, b, c, d):
        dx, dy = a - c, b - d
        return dx * dx + dy * dy
    def mobility(x, y):
        m = 0
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if ok(nx, ny):
                m += 1
        return m
    def nearest_obstacle_dist2(x, y):
        best = 10**9
        for ox2, oy2 in obstacles:
            d = dist2(x, y, ox2, oy2)
            if d < best:
                best = d
        return best if best != 10**9 else 10**9

    # Deterministic target corner for evader
    if is_evader:
        tx, ty = max(corners, key=lambda c: dist2(c[0], c[1], ox, oy))
    else:
        tx, ty = None, None

    best_move = (0, 0)
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            nx, ny = sx, sy  # engine would keep us in place; model that deterministically

        d_opp = dist2(nx, ny, ox, oy)
        mob = mobility(nx, ny)

        if is_evader:
            # Push away from pursuer while drifting to the chosen corner; avoid tight obstacle proximity.
            d_corner = dist2(nx, ny, tx, ty)
            score = d_opp + 0.35 * d_corner + 0.07 * mob - 0.01 * nearest_obstacle_dist2(nx, ny)
        else:
            # Pursuer: greedy capture pressure with slight preference for higher local mobility.
            score = -d_opp + 0.03 * mob

        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]