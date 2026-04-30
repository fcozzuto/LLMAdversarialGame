def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])
    obs = set((x, y) for x, y in obstacles)

    def clamp(v, lo, hi):
        return lo if v < lo else hi if v > hi else v

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    # If no info, stay.
    if not resources:
        return [0, 0]

    best = None
    for rx, ry in resources:
        if (rx, ry) in obs:
            continue
        dme = dist((sx, sy), (rx, ry))
        do = dist((ox, oy), (rx, ry))
        # Prefer resources we reach earlier; lightly favor those closer overall.
        score = (dme - 0.75 * do) + 0.02 * dme
        if best is None or score < best[0]:
            best = (score, rx, ry)

    _, tx, ty = best
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    # Try intended move; then deterministic fallback directions.
    candidates = [
        (dx, dy),
        (dx, 0),
        (0, dy),
        (dx, -dy),
        (-dx, dy),
        (0, 0),
    ]
    tried = set()
    for mx, my in candidates:
        if (mx, my) in tried:
            continue
        tried.add((mx, my))
        nx, ny = sx + mx, sy + my
        nx = clamp(nx, 0, w - 1)
        ny = clamp(ny, 0, h - 1)
        if valid(nx, ny):
            return [mx, my]

    # Final safety: pick any valid neighboring step deterministically.
    for mx, my in [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]:
        nx, ny = sx + mx, sy + my
        nx = clamp(nx, 0, w - 1)
        ny = clamp(ny, 0, h - 1)
        if valid(nx, ny):
            return [mx, my]

    return [0, 0]