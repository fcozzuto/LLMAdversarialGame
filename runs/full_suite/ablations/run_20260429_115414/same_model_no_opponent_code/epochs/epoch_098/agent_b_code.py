def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

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

    def king_dist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = (10**9, 10**9, 10**9)
        bestm = (0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d = king_dist(nx, ny, cx, cy)
            key = (d, dx, dy)
            if key < best:
                best, bestm = key, (dx, dy)
        return [int(bestm[0]), int(bestm[1])]

    best_overall = (10**18, 10**18, 10**18, 0, 0)
    best_move = (0, 0)

    for dxm, dym in moves:
        nx, ny = sx + dxm, sy + dym
        if not valid(nx, ny):
            continue

        # For each resource, prefer one where we are closer than opponent (maximize relative advantage),
        # but still keep absolute distance small; tie-break by position.
        best_key = None
        for tx, ty in resources:
            ds = king_dist(nx, ny, tx, ty)
            do = king_dist(ox, oy, tx, ty)
            rel = ds - do  # smaller is better (we catch first)
            key = (rel, ds, tx, ty)
            if best_key is None or key < best_key:
                best_key = key

        if best_key is None:
            continue
        # Slight preference to reduce distance to chosen target next: already in key; add move tie-break
        overall = (best_key[0], best_key[1], best_key[2], best_key[3], dxm, dym)
        if overall < best_overall:
            best_overall = overall
            best_move = (dxm, dym)

    return [int(best_move[0]), int(best_move[1])]