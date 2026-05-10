def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((p[0], p[1]) for p in observation.get("obstacles", []) or [])
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    resources = observation.get("resources", None) or []
    targets = []
    if resources:
        for r in resources:
            try:
                targets.append((r[0], r[1]))
            except Exception:
                pass
    else:
        targets = [(ox, oy)]

    def best_target(tx, ty):
        best = (10**9, 0)
        for px, py in targets:
            d = abs(px - tx) if abs(px - tx) > abs(py - ty) else abs(py - ty)
            if d < best[0]:
                best = (d, (px, py))
        return best[1]

    def score(x, y):
        tx, ty = best_target(x, y)
        return abs(tx - x) + abs(ty - y) - 0.01 * (abs(ox - x) + abs(oy - y))

    best = None
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        v = score(nx, ny)
        if best is None or v < best_val or (v == best_val and (dx, dy) < best):
            best = (dx, dy)
            best_val = v

    if best is None:
        return [0, 0]
    return [best[0], best[1]]