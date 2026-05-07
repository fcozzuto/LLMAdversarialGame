def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p is not None and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources:
        return [0, 0]

    # Pick target that favors us: (opp_dist - our_dist), avoid targets exactly on opponent row too often.
    best_t = None
    best_key = None
    for tx, ty in resources:
        if (tx, ty) in obstacles:
            continue
        sd = cheb(sx, sy, tx, ty)
        od = cheb(ox, oy, tx, ty)
        row_pen = -0.5 if ty == oy else 0.2
        key = (od - sd + row_pen, -sd, -tx, -ty)
        if best_key is None or key > best_key:
            best_key = key
            best_t = (tx, ty)
    if best_t is None:
        return [0, 0]
    tx, ty = best_t

    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if legal(nx, ny):
                # Prefer immediate improvement and denial against opponent.
                myd = cheb(nx, ny, tx, ty)
                opd = cheb(ox, oy, tx, ty)
                # Also softly steer away from obstacles by penalizing moves that reduce clearance.
                # (cheap proxy: fewer blocked neighbor cells).
                blocked = 0
                for adx in (-1, 0, 1):
                    for ady in (-1, 0, 1):
                        if adx == 0 and ady == 0:
                            continue
                        xx, yy = nx + adx, ny + ady
                        if not legal(xx, yy):
                            blocked += 1
                # Key: maximize our advantage; avoid getting boxed (lower blocked).
                key = (opd - myd, -myd, -blocked, -dx, -dy)
                candidates.append((key, dx, dy))
    if not candidates:
        return [0, 0]
    candidates.sort(reverse=True)
    return [candidates[0][1], candidates[0][2]]