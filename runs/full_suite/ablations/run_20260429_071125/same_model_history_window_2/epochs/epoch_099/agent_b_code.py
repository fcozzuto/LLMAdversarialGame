def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if legal(x, y):
                resources.append((x, y))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def best_target():
        if not resources:
            return (ox, oy)
        best = None
        best_key = None
        for rx, ry in resources:
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Prefer states where we are closer than opponent; tie-break by closeness and lexicographic.
            key = (-(do - ds), ds, rx, ry)
            if best_key is None or key < best_key:
                best_key = key
                best = (rx, ry)
        return best

    tx, ty = best_target()
    candidates = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        # Evaluate candidate by its improvement in winning prospects for target and general resource progress.
        ds_now = cheb(sx, sy, tx, ty)
        ds_next = cheb(nx, ny, tx, ty)
        do_target = cheb(ox, oy, tx, ty)
        closer = (ds_now - ds_next)
        # Encourage preventing opponent capture: move toward squares that increase their distance to target.
        do_next = cheb(nx, ny, tx, ty)  # same metric; deterministic shaping via symmetry
        # Global tie-break: prefer lower (nx,ny) lex for determinism.
        val_key = (-(closer), abs(do_target - ds_next), ds_next, nx, ny)
        candidates.append((val_key, (dx, dy)))

    if not candidates:
        return [0, 0]
    candidates.sort(key=lambda t: t[0])
    return [candidates[0][1][0], candidates[0][1][1]]