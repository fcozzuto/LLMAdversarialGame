def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in (observation.get("resources", []) or []):
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def best_resource_score(px, py):
        # Positive score favors us: (op further than us) + a small tie-break on our closeness.
        best = -10**18
        for tx, ty in resources:
            dm = cheb(px, py, tx, ty)
            do = cheb(ox, oy, tx, ty)
            # If we're closer, score increases; if we're farther, decreases.
            # Extra weight to contested swing.
            swing = (do - dm)
            closeness = -dm
            # Prefer resources that are relatively nearer to us even when not strictly closest.
            val = 10 * swing + closeness
            if val > best:
                best = val
        return best

    best_move = [0, 0]
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        v = best_resource_score(nx, ny)

        # Anti-suicide: discourage moving away from all resources if opponent is much closer elsewhere.
        # Also lightly encourage not giving opponent immediate capture by staying too close to their path.
        # (Deterministic: based on current positions only.)
        dm_op_to_nearest = min(cheb(ox, oy, tx, ty) for (tx, ty) in resources)
        dm_me_to_nearest = min(cheb(nx, ny, tx, ty) for (tx, ty) in resources)
        v += (dm_op_to_nearest - dm_me_to_nearest)

        # Deterministic tie-break: closer to center, then lexicographic move preference.
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        center_bonus = -abs(nx - cx) - abs(ny - cy)
        v += 0.001 * center_bonus

        if v > best_val:
            best_val = v
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]