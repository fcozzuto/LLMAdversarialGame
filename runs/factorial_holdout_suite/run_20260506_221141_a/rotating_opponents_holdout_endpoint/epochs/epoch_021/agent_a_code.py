def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles_in = observation.get("obstacles") or []

    obstacles = set()
    for p in obstacles_in:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    legal = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny):
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    if not resources:
        return [0, 0]

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def resource_score(px, py, rx, ry):
        ds = dist(px, py, rx, ry)
        do = dist(ox, oy, rx, ry)
        slack = do - ds  # positive means we are closer (or would be after tie-break)
        center = - (abs(rx - cx) + abs(ry - cy)) * 0.01
        # Encourage winning a resource; if can't, still move toward good options.
        return slack * 100 - ds + center

    def best_score(px, py):
        best = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            sc = resource_score(px, py, rx, ry)
            if best is None or sc > best:
                best = sc
        return best if best is not None else -10**9

    # If we are currently about to lose everything (opponent closer to all), bias to nearest "denial" move.
    best_here = best_score(sx, sy)
    if best_here < 0:
        # Move to increase minimum (do-ds) over resources by one step.
        target = None
        best_min = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            ds = dist(sx, sy, rx, ry)
            do = dist(ox, oy, rx, ry)
            slack = do - ds
            if target is None or slack > best_min[0]:
                target = (rx, ry)
                best_min = (slack, rx, ry)
        if target is not None:
            rx, ry = target
            # Greedy step that moves closer to target while staying legal.
            cand = sorted(legal, key=lambda t: (dist(t[2], t[3], rx, ry), (t[0], t[1])))
            return [int(cand[0][0]), int(cand[0][1])]

    # Otherwise, pick the legal move that maximizes best resource value from the next position.
    legal.sort(key=lambda t: (-(best_score(t[2], t[3]) if resources else -10**9), t[0], t[1]))
    return [int(legal[0][0]), int(legal[0][1])]