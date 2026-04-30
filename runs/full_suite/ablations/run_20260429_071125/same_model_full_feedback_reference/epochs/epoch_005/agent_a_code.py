def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles_in = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles_in:
        if p is not None and len(p) >= 2:
            x, y = p[0], p[1]
            if x is not None and y is not None:
                x, y = int(x), int(y)
                if 0 <= x < w and 0 <= y < h:
                    obs.add((x, y))

    resources_in = observation.get("resources", []) or []
    resources = []
    for p in resources_in:
        if p is not None and len(p) >= 2:
            x, y = p[0], p[1]
            if x is not None and y is not None:
                x, y = int(x), int(y)
                if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                    resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def nearest_res_dist(x, y):
        if not resources:
            return None
        best = 10**9
        for rx, ry in resources:
            d = man(x, y, rx, ry)
            if d < best:
                best = d
        return best

    if not inb(sx, sy):
        return [0, 0]

    best = -10**18
    best_move = [0, 0]
    cur_r = nearest_res_dist(sx, sy)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        on_res = (nx, ny) in resources
        dres = 0 if on_res else nearest_res_dist(nx, ny)
        dop = man(nx, ny, ox, oy)

        # Heuristic: prioritize taking resources; otherwise reduce distance to resources,
        # while also keeping distance from opponent to avoid contesting their capture route.
        score = 0.0
        if on_res:
            score += 10**6
        if dres is not None:
            score += -3.0 * dres
            if cur_r is not None:
                score += 0.8 * (cur_r - dres)
        score += 1.2 * dop

        # Small deterministic tie-break: prefer moves that reduce coordinate sum distance to center.
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        score += -0.01 * (abs(nx - cx) + abs(ny - cy))

        if score > best:
            best = score
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]