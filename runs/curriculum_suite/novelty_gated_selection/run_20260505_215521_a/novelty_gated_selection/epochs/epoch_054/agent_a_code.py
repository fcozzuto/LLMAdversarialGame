def choose_move(observation):
    w = int(observation.get("grid_width", 0) or 0)
    h = int(observation.get("grid_height", 0) or 0)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    if w <= 0 or h <= 0:
        return [0, 0]

    obst = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obst.add((int(p[0]), int(p[1])))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            resources.append((int(r[0]), int(r[1])))

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]
    cx, cy = (w - 1) // 2, (h - 1) // 2

    def nearest_res_dist(x, y):
        if not resources:
            return 10**9
        best = 10**9
        for rx, ry in resources:
            d = abs(x - rx) + abs(y - ry)
            if d < best:
                best = d
        return best

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    best = None
    bx, by = sx, sy
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obst:
            continue
        dres = nearest_res_dist(nx, ny)
        dob = abs(nx - ox) + abs(ny - oy)
        center_bias = -0.1 * (abs(nx - cx) + abs(ny - cy))
        # Prefer closer to resources; strongly prefer not being near opponent.
        val = (10**6 if dres == 0 else 0) - 10 * dres + 3 * dob + center_bias
        key = (val, -dx, -dy)
        if best is None or key > best:
            best = key
            bx, by = nx, ny

    return [bx - sx, by - sy]