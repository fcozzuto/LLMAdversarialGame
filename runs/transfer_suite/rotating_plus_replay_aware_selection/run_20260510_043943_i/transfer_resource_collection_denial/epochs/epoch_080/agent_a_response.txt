def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cell_ok(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def man(ax, ay, bx, by):
        d1 = ax - bx
        if d1 < 0:
            d1 = -d1
        d2 = ay - by
        if d2 < 0:
            d2 = -d2
        return d1 + d2

    if not resources:
        return [0, 0]

    deltas = [(-1, -1), (0, -1), (1, -1),
              (-1, 0),  (0, 0),  (1, 0),
              (-1, 1),  (0, 1),  (1, 1)]

    best = None
    best_delta = [0, 0]

    center_bias = lambda x, y: -abs(x - (w - 1) / 2.0) - abs(y - (h - 1) / 2.0)

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not cell_ok(nx, ny):
            nx, ny = sx, sy
            dx, dy = 0, 0

        score = -10**9
        for rx, ry in resources:
            if not cell_ok(rx, ry):
                continue
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            # Race heuristic: reward arriving sooner; strongly penalize being at/behind.
            rel = od - sd
            if rel >= 2:
                s = 6000 + 200 * rel - sd + 3 * center_bias(nx, ny)
            elif rel == 1:
                s = 2000 + 80 * rel - sd + 2 * center_bias(nx, ny)
            elif rel == 0:
                s = -50 - sd + 1 * center_bias(nx, ny)
            else:
                s = -1200 * (-rel) - 2 * sd + 0.5 * center_bias(nx, ny)
            if s > score:
                score = s

        if best is None or score > best:
            best = score
            best_delta = [dx, dy]
        elif score == best:
            # Deterministic tie-break: prefer staying if same, else lowest dx, then lowest dy.
            if (best_delta[0], best_delta[1]) == (0, 0) and (dx, dy) != (0, 0):
                continue
            if dx < best_delta[0] or (dx == best_delta[0] and dy < best_delta[1]):
                best_delta = [dx, dy]

    return [int(best_delta[0]), int(best_delta[1])]