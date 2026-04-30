def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    best = (-(10**18), 0, 0)  # (value, our_best, -sep)
    best_move = (0, 0)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue

        our_best = 10**9
        best_gap = -10**9  # dist_op - dist_us for best resource
        for rx, ry in resources:
            du = dist(nx, ny, rx, ry)
            do = dist(ox, oy, rx, ry)
            if du < our_best:
                our_best = du
            gap = do - du
            if gap > best_gap:
                best_gap = gap

        sep = dist(nx, ny, ox, oy)
        # Prefer moves where we are closer than opponent to some resource, and then closer to resources overall.
        value = (best_gap * 1000) - our_best * 3 + sep * 1
        key = (value, -our_best, sep)
        if key > best:
            best = (value, our_best, sep)
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]