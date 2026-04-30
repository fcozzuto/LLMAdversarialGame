def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    if not resources:
        # Default: move away from opponent slightly to avoid congestion
        dx = -1 if sx > ox else (1 if sx < ox else 0)
        dy = -1 if sy > oy else (1 if sy < oy else 0)
        return [dx, dy]

    def clamp(v, lo, hi):
        return lo if v < lo else (hi if v > hi else v)

    # Choose nearest resource deterministically
    best_t = None
    best_key = None
    for rx, ry in resources:
        if (rx < 0) or (rx >= w) or (ry < 0) or (ry >= h):
            continue
        d = (rx - sx) * (rx - sx) + (ry - sy) * (ry - sy)
        key = (d, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_t = (rx, ry)

    tx, ty = best_t
    deltas = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            nx = clamp(nx, 0, w - 1)
            ny = clamp(ny, 0, h - 1)
            if (nx, ny) in obstacles:
                continue
            # Primary: reduce distance to target; Secondary: avoid staying; Tertiary: stable tie-break
            nd = (tx - nx) * (tx - nx) + (ty - ny) * (ty - ny)
            stay_pen = 0 if (dx == 0 and dy == 0) else -1
            # Mildly prefer moves that don't step toward opponent too aggressively
            od = (ox - nx) * (ox - nx) + (oy - ny) * (oy - ny)
            score = (nd, -stay_pen, -od, dx, dy)
            deltas.append((score, [dx, dy]))

    deltas.sort(key=lambda x: x[0])
    if deltas:
        return deltas[0][1]
    return [0, 0]