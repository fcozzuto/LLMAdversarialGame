def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obst = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                resources.append((x, y))

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def mdist(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    candidates = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if free(nx, ny):
            candidates.append((dx, dy, nx, ny))

    if not candidates:
        return [0, 0]

    if resources:
        best = None
        best_score = None
        for dx, dy, nx, ny in candidates:
            # Prefer reducing distance to nearest resource; also prefer staying away from opponent.
            dres = min(mdist((nx, ny), r) for r in resources)
            dop = mdist((nx, ny), (ox, oy))
            score = (-dres * 100) + (dop)  # integer-like preference
            if best is None or score > best_score:
                best_score = score
                best = (dx, dy)
        return [best[0], best[1]]

    # If no resources known, drift away from opponent deterministically toward center
    cx, cy = (w - 1) // 2, (h - 1) // 2
    best = None
    best_score = None
    for dx, dy, nx, ny in candidates:
        dop = mdist((nx, ny), (ox, oy))
        dcen = mdist((nx, ny), (cx, cy))
        score = (dop * 100) - (dcen)  # maximize distance from opponent, then toward center
        if best is None or score > best_score:
            best_score = score
            best = (dx, dy)
    return [best[0], best[1]]