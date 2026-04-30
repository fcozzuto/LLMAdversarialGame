def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    if resources:
        def dist(a, b):
            return max(abs(a[0]-b[0]), abs(a[1]-b[1]))
        # Deterministically pick target: nearest resource; tie-break by coordinates
        tgt = min(resources, key=lambda r: (dist((sx, sy), tuple(r)), tuple(r)))
        tx, ty = tgt
    else:
        tx, ty = (w - 1) / 2.0, (h - 1) / 2.0

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    best = None
    best_score = None
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not in_bounds(nx, ny):
                continue
            blocked = (nx, ny) in obstacles
            # If blocked, we strongly discourage; engine would keep us anyway
            d_t = max(abs(nx - tx), abs(ny - ty)) if resources else (abs(nx - tx) + abs(ny - ty))
            d_o = max(abs(nx - ox), abs(ny - oy))
            on_res = 1 if resources and any(nx == r[0] and ny == r[1] for r in resources) else 0
            # Score: lower is better for move selection
            score = (0 if not blocked else 10000) + d_t - (0.15 * d_o) - (50 * on_res) + (0.01 * (abs(dx) + abs(dy)))
            if best_score is None or score < best_score or (score == best_score and (dx, dy) < best):
                best_score = score
                best = (dx, dy)
    if best is None:
        return [0, 0]
    return [best[0], best[1]]