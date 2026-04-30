def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    if resources:
        def dist(a, b):  # Chebyshev for grid with diagonal moves
            return max(abs(a[0] - b[0]), abs(a[1] - b[1]))
        best = None
        best_key = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            d1 = dist((sx, sy), (rx, ry))
            d2 = dist((ox, oy), (rx, ry))
            # Prefer resources we're closer to; deterministic tie-break by coords
            key = (d1 - d2, d1, rx, ry)
            if best is None or key < best_key:
                best = (rx, ry)
                best_key = key
        tx, ty = best
    else:
        # No visible resources: move toward center to avoid stalling
        tx, ty = (w - 1) // 2, (h - 1) // 2

    dx_raw = 0 if tx == sx else (1 if tx > sx else -1)
    dy_raw = 0 if ty == sy else (1 if ty > sy else -1)

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                moves.append((dx, dy))
    if not moves:
        return [0, 0]

    def score_move(dx, dy):
        nx, ny = sx + dx, sy + dy
        # Primary: get closer to target
        return max(abs(tx - nx), abs(ty - ny))

    # Prefer direct step; then best distance; deterministic tie-break
    direct = (dx_raw, dy_raw)
    if direct in moves:
        return [direct[0], direct[1]]
    best_m = None
    best_s = None
    for dx, dy in moves:
        s = score_move(dx, dy)
        if best_s is None or s < best_s or (s == best_s and (dx, dy) < best_m):
            best_s = s
            best_m = (dx, dy)
    return [best_m[0], best_m[1]]