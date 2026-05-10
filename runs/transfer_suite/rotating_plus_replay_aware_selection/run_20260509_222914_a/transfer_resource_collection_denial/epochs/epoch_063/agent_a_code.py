def choose_move(observation):
    w = int(observation.get("grid_width", 0) or 0)
    h = int(observation.get("grid_height", 0) or 0)
    if w <= 0 or h <= 0:
        return [0, 0]

    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            ax, ay = int(p[0]), int(p[1])
            if 0 <= ax < w and 0 <= ay < h:
                obs.add((ax, ay))

    resources = []
    for p in (observation.get("resources") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            rx, ry = int(p[0]), int(p[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obs:
                resources.append((rx, ry))
    if not resources:
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def manhattan(x1, y1, x2, y2):
        d1 = x1 - x2
        if d1 < 0:
            d1 = -d1
        d2 = y1 - y2
        if d2 < 0:
            d2 = -d2
        return d1 + d2

    def score_at(px, py):
        best = None
        for rx, ry in resources:
            sd = manhattan(px, py, rx, ry)
            od = manhattan(ox, oy, rx, ry)
            v = (od - sd, -sd)  # maximize (opp closer advantage), then minimize self distance
            if best is None or v > best:
                best = v
        return best

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    best_first = (0, 0)
    best_val = None

    for dx1, dy1 in moves:
        nx1, ny1 = sx + dx1, sy + dy1
        if not valid(nx1, ny1):
            nx1, ny1 = sx, sy

        best_second = None
        for dx2, dy2 in moves:
            nx2, ny2 = nx1 + dx2, ny1 + dy2
            if valid(nx2, ny2):
                v = score_at(nx2, ny2)
                if best_second is None or v > best_second:
                    best_second = v
            else:
                v = score_at(nx1, ny1)
                if best_second is None or v > best_second:
                    best_second = v

        v1 = score_at(nx1, ny1)
        v = (best_second[0], best_second[1], v1[1], -abs(nx1 - (w - 1) / 2) - abs(ny1 - (h - 1) / 2))
        if best_val is None or v > best_val:
            best_val = v
            best_first = (dx1, dy1)

    return [int(best_first[0]), int(best_first[1])]