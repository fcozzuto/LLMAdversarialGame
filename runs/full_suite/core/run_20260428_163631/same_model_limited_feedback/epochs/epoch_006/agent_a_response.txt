def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((p[0], p[1]) for p in observation.get("obstacles", []))
    resources = observation.get("resources", [])
    dxs = (-1, 0, 1)
    dys = (-1, 0, 1)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        # Chebyshev (good for king-like moves)
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    # Pick a target resource where we are relatively closer than opponent
    target = None
    if resources:
        best = None
        for rx, ry in resources:
            d_s = dist((sx, sy), (rx, ry))
            d_o = dist((ox, oy), (rx, ry))
            # Prefer resources closer to us; bias away from those opponent is much closer to
            score = d_s - 0.9 * d_o + 0.02 * (rx + 7 * ry)
            # Deterministic tie-break by coordinates
            key = (score, d_s, rx, ry)
            if best is None or key < best[0]:
                best = (key, (rx, ry))
        target = best[1]

    if target is None:
        tx, ty = ox, oy
    else:
        tx, ty = target

    best_move = [0, 0]
    best_key = None
    for dx in dxs:
        for dy in dys:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            if (nx, ny) in obstacles:
                continue
            d1 = dist((nx, ny), (tx, ty))
            # Prefer decreasing distance; then closer to opponent; then deterministic direction preference
            opp_d = dist((nx, ny), (ox, oy))
            key = (d1, opp_d, dx, dy)
            if best_key is None or key < best_key:
                best_key = key
                best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]