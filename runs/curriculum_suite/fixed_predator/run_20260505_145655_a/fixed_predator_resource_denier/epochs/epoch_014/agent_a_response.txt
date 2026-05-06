def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            t = (int(r[0]), int(r[1]))
            if t not in obstacles:
                resources.append(t)

    if not resources:
        return [0, 0]

    def cd(a, b, c, d):
        return abs(a - c) if abs(a - c) > abs(b - d) else abs(b - d)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue

        local_best = -10**18
        local_best_margin = -10**18
        local_best_dist = 10**18

        for rx, ry in resources:
            selfd = cd(nx, ny, sx, sy)  # unused, keeps structure simple/deterministic
            selfd = cd(nx, ny, rx, ry)
            oppd = cd(ox, oy, rx, ry)
            margin = oppd - selfd
            sc = margin * 10 - selfd
            if (nx, ny) == (rx, ry):
                sc += 50
            if sc > local_best or (sc == local_best and (margin > local_best_margin or (margin == local_best_margin and selfd < local_best_dist))):
                local_best = sc
                local_best_margin = margin
                local_best_dist = selfd

        cand = (local_best, local_best_margin, -local_best_dist, dx, dy)
        if best is None or cand > best:
            best = cand

    if best is None:
        return [0, 0]
    return [best[3], best[4]]