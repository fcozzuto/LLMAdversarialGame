def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if (sx, sy) in resources or not resources:
        return [0, 0]

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def key_target(t):
        sd = man((sx, sy), t)
        od = man((ox, oy), t)
        # Prefer targets where we can beat opponent sooner, avoid opponent's current row a bit.
        row_pen = 6 if t[1] == oy else 0
        col_pen = 2 if t[0] == ox else 0
        # Also lightly prefer closer targets when advantage is similar.
        return (row_pen + col_pen + (sd - od), sd, t[0], t[1])

    target = min(resources, key=key_target)
    tx, ty = target

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        # Avoid stepping into opponent's immediate reach too often.
        opp_dist = man((nx, ny), (ox, oy))
        step_sd = man((nx, ny), (tx, ty))
        # Prefer being closer to target; prefer larger separation from opponent; avoid opponent row.
        row_bad = 3 if ny == oy else 0
        score = (row_bad + step_sd - (opp_dist // 2), step_sd, -opp_dist, nx, ny)
        if best is None or score < best[0]:
            best = (score, dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[1]), int(best[2])]