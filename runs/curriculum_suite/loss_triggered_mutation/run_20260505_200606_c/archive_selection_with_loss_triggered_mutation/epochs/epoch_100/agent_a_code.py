def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    resources = observation.get("resources", []) or []
    obstacles_raw = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles_raw:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            px, py = int(p[0]), int(p[1])
            if 0 <= px < w and 0 <= py < h:
                obs.add((px, py))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    if not resources:
        return [0, 0]

    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obs:
                res.append((rx, ry))
    if not res:
        return [0, 0]

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    def md(a, b, c, d):
        ax = a - c
        if ax < 0:
            ax = -ax
        ay = b - d
        if ay < 0:
            ay = -ay
        return ax + ay

    best_key = None
    best_move = (0, 0)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        best_for_move = None
        for rx, ry in res:
            sd = md(nx, ny, rx, ry)
            od = md(ox, oy, rx, ry)
            margin = sd - od  # smaller is better (more likely to reach first)
            key = (margin, sd, -od)
            if best_for_move is None or key < best_for_move:
                best_for_move = key
        if best_for_move is None:
            continue
        # small tiebreaker: prefer staying closer to center (deterministic)
        cx = (w - 1) / 2.0
        cy = (h - 1) / 2.0
        center_pen = (abs(nx - cx) + abs(ny - cy)) * 1e-3
        full_key = (best_for_move[0], best_for_move[1], best_for_move[2], center_pen, dx, dy)
        if best_key is None or full_key < best_key:
            best_key = full_key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]