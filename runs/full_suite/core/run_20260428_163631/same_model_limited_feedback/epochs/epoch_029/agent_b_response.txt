def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def clamp(v, lo, hi):
        return lo if v < lo else hi if v > hi else v

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def manh(a, b, c, d):
        return abs(a - c) + abs(b - d)

    if not resources:
        # fallback: move toward center
        cx, cy = (w - 1) // 2, (h - 1) // 2
        tx, ty = cx, cy
    else:
        best = None
        for rx, ry in resources:
            d1 = manh(sx, sy, rx, ry)
            d2 = manh(ox, oy, rx, ry)
            score = (d1 - d2, d1, rx, ry)
            if best is None or score < best[0]:
                best = (score, rx, ry)
        tx, ty = best[1], best[2]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        dist = manh(nx, ny, tx, ty)
        # Prefer reducing distance; if equal, keep deterministic ordering by dx,dy
        cand = (dist, dx, dy)
        if best_move is None or cand < best_move[0]:
            best_move = (cand, dx, dy)

    if best_move is None:
        return [0, 0]
    return [int(best_move[1]), int(best_move[2])]