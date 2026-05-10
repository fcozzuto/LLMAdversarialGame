def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])

    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if inb(x, y) and (x, y) not in obs:
                res.append((x, y))
    if not res:
        return [0, 0]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def dist(a, b, x, y):
        return abs(a - x) + abs(b - y)

    best_delta = (0, 0)
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        # Pick the resource we can contest best after this move.
        # Score favors: we being earlier than opponent, and reaching closer targets.
        local_best = None
        for (rx, ry) in res:
            sd = dist(nx, ny, rx, ry)
            od = dist(ox, oy, rx, ry)
            margin = od - sd
            # Encourage immediate pickup and shorter travel deterministically.
            score = (margin, -sd, -((sd <= 1) * 1), -(sd == 0))
            if local_best is None or score > local_best:
                local_best = score

        move_score = local_best
        if best_score is None or move_score > best_score:
            best_score = move_score
            best_delta = (dx, dy)

    return [int(best_delta[0]), int(best_delta[1])]