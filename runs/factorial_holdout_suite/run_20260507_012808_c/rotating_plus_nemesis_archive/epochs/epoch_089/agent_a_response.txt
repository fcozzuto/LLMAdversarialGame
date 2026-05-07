def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx * dx + dy * dy

    moves = [(-1, 0), (0, -1), (0, 0), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    if not resources:
        return [0, 0]

    # Choose best target deterministically by advantage: (opp_dist - self_dist) then closer self then coord.
    # Use squared distances for speed/determinism.
    best_t = None
    best = None
    for (rx, ry) in resources:
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        adv = od - sd
        key = (adv, -sd, -rx, -ry)
        if best is None or key > best:
            best = key
            best_t = (rx, ry)

    rx, ry = best_t

    # Pick move that maximizes same advantage after move; break ties by minimizing self distance.
    best_m = (0, 0)
    best_m_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        sd2 = man(nx, ny, rx, ry)
        od2 = man(ox, oy, rx, ry)  # opponent assumed stationary for 1-step evaluation
        adv2 = od2 - sd2
        key = (adv2, -sd2, -nx, -ny)
        if best_m_key is None or key > best_m_key:
            best_m_key = key
            best_m = (dx, dy)

    return [int(best_m[0]), int(best_m[1])]