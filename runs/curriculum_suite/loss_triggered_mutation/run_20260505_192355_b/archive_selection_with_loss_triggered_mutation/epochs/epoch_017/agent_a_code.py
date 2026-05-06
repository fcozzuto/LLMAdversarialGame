def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles", []) or []
    obst = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = observation.get("resources", []) or []
    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                res.append((x, y))

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not res:
        for dx, dy in dirs:
            if free(sx + dx, sy + dy):
                return [dx, dy]
        return [0, 0]

    # Choose target where we can arrive earlier (or at least not much later) than opponent; tie-break by distance.
    best = None
    for x, y in res:
        sd = man(sx, sy, x, y)
        od = man(ox, oy, x, y)
        lead = od - sd  # positive means we are closer
        key = (-(lead), sd, abs(x - (w - 1 - ox)) + abs(y - (h - 1 - oy)), x, y)
        if best is None or key < best[0]:
            best = (key, (x, y))
    tx, ty = best[1]

    # Move one step toward the target while keeping it free; tie-break by maximizing lead improvement.
    best_move = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        nsd = man(nx, ny, tx, ty)
        nod = man(ox, oy, tx, ty)
        lead_after = nod - nsd
        key = (-lead_after, nsd, dx*dx + dy*dy, nx, ny)
        if best_move is None or key < best_move[0]:
            best_move = (key, [dx, dy])

    if best_move is None:
        return [0, 0]
    return best_move[1]