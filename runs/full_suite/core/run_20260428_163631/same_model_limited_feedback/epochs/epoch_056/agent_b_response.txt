def choose_move(observation):
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)

    deltas = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    def in_bounds(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def dist2(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return dx * dx + dy * dy

    # Pick nearest resource deterministically (tie: lowest x then lowest y)
    if resources:
        target = min(resources, key=lambda p: (dist2((x, y), p), p[0], p[1]))
        tx, ty = target
    else:
        tx, ty = (w - 1) / 2.0, (h - 1) / 2.0

    best = None
    best_key = None
    for dx, dy in deltas:
        nx, ny = x + dx, y + dy
        if not in_bounds(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue

        # Prefer approaching target, and slightly prefer staying away from opponent
        d_target = dist2((nx, ny), (tx, ty)) if resources else ((nx - tx) ** 2 + (ny - ty) ** 2)
        d_opp = dist2((nx, ny), (ox, oy))
        # Extra tie-breakers for determinism and to avoid oscillation: prefer smaller move magnitude, then fixed ordering
        mag = abs(dx) + abs(dy)
        key = (d_target, -d_opp, mag, dx, dy)

        if best_key is None or key < best_key:
            best_key = key
            best = [dx, dy]

    return best if best is not None else [0, 0]