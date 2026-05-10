def choose_move(observation):
    w = int(observation.get("grid_width", 0) or 0)
    h = int(observation.get("grid_height", 0) or 0)
    if w <= 0 or h <= 0:
        return [0, 0]

    sx, sy = observation.get("self_position", (0, 0))
    sx, sy = int(sx), int(sy)

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

    ox, oy = observation.get("opponent_position", (0, 0))
    ox, oy = int(ox), int(oy)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    best_move = (0, 0)
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            continue

        my = (nx, ny)
        best_for_move = None
        for r in resources:
            sd = abs(r[0] - nx) + abs(r[1] - ny)
            od = abs(r[0] - ox) + abs(r[1] - oy)
            gap = od - sd  # positive means we are closer
            val = (gap, -sd, -abs(r[0] - ox) - abs(r[1] - oy))
            if best_for_move is None or val > best_for_move:
                best_for_move = val

        if best_for_move is None:
            continue
        if best_val is None or best_for_move > best_val:
            best_val = best_for_move
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]