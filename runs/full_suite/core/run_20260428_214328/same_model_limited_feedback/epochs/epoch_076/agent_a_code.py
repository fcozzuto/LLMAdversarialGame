def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set((p[0], p[1]) for p in observation["obstacles"])

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    dirs = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    if not resources:
        # Drift toward center if no resources
        tx, ty = (w - 1) / 2, (h - 1) / 2
        best = (1e9, 0, 0)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny) or (nx, ny) in obstacles:
                continue
            val = abs(nx - tx) + abs(ny - ty)
            if val < best[0]:
                best = (val, dx, dy)
        return [best[1], best[2]]

    # Select target resource by race heuristic: prefer close to us and far from opponent.
    best_res = None
    best_key = None
    for rx, ry in resources:
        ds = dist((sx, sy), (rx, ry))
        do = dist((ox, oy), (rx, ry))
        key = (ds - do, ds, rx, ry)  # smaller is better
        if best_key is None or key < best_key:
            best_key = key
            best_res = (rx, ry)

    rx, ry = best_res

    best = None  # (score, dx, dy)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue
        ds_next = abs(nx - rx) + abs(ny - ry)
        do_now = abs(ox - rx) + abs(oy - ry)
        # If we're already behind, prioritize reducing the gap aggressively.
        behind = ds_next - do_now
        penalty = 0
        if behind > 0:
            penalty = behind * 0.2
        # Prefer moves that don't overshoot diagonally when equally good.
        diag_pen = 0.05 if dx != 0 and dy != 0 else 0
        score = ds_next + penalty + diag_pen
        cand = (score, abs(dx) + abs(dy), dx, dy)
        if best is None or cand < best:
            best = cand

    return [int(best[2]), int(best[3])]