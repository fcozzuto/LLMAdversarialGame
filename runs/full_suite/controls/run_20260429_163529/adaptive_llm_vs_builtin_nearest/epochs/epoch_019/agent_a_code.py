def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    resources = observation.get("resources") or []
    res = []
    for r in resources:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))
    if not res:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def cheb(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    def nearest_dist(x, y):
        best = 10**9
        for rx, ry in res:
            d = cheb(x, y, rx, ry)
            if d < best:
                best = d
        return best

    # Tie-break deterministically by move order; favor moves that decrease our nearest-resource distance
    best_move = (0, 0)
    best_score = -10**18
    my0 = nearest_dist(sx, sy)
    op0 = nearest_dist(ox, oy)

    for mx, my in moves:
        nx, ny = sx + mx, sy + my
        if not inside(nx, ny):
            # avoid obstacle cell to prevent engine "stays" unless all blocked
            continue

        my = nearest_dist(nx, ny)
        op = nearest_dist(ox, oy)

        # Maximize lead: opponent closer -> worse for us
        score = (op - my) * 100 - my

        # Small shaping: prefer moves that reduce absolute distance to the closest resource from our next position
        if my < my0:
            score += 5
        # Prefer not to move away from center-ish towards resources: deterministic slight penalty for larger coordinate magnitude
        score -= (abs(nx - (w // 2)) + abs(ny - (h // 2))) * 0.01

        if score > best_score:
            best_score = score
            best_move = (mx, my)

    if best_move == (0, 0):
        # If all moves blocked (unlikely), just try staying; still deterministic.
        return [0, 0]
    return [best_move[0], best_move[1]]