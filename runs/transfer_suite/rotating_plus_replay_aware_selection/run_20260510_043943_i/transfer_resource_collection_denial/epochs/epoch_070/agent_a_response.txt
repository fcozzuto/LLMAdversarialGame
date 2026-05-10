def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cell_ok(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def dist(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    if not resources:
        return [0, 0]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # pick best target: prioritize winning/contested resources (we must be strictly earlier)
    best = None
    best_key = None
    for r in resources:
        rx, ry = r
        if not cell_ok(rx, ry):
            continue
        sd = dist((sx, sy), (rx, ry))
        od = dist((ox, oy), (rx, ry))
        advantage = od - sd  # bigger => more likely we arrive first
        # tie-break: closer to us; deterministic final order via (sd, rx, ry)
        key = (-(0 if advantage > 0 else 1), -advantage, sd, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    if best is None:
        return [0, 0]

    tx, ty = best

    # choose move that most reduces distance to the chosen target, avoiding obstacles
    best_m = (0, 0)
    best_d = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not cell_ok(nx, ny):
            nx, ny = sx, sy
            dx, dy = 0, 0
        d = dist((nx, ny), (tx, ty))
        key = (d, abs(dx) + abs(dy), dx, dy)
        if best_d is None or key < (best_d,):
            best_d = d
            best_m = (dx, dy)

    return [int(best_m[0]), int(best_m[1])]