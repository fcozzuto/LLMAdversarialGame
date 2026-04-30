def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
    obstacles.discard((sx, sy))
    obstacles.discard((ox, oy))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if (sx, sy) in set(resources):
        return [0, 0]

    # New strategic shift: lock on to resources where we are faster than the opponent.
    best = None
    best_key = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        margin = do - ds  # positive means we can reach earlier/tie
        # Deterministic tie-breakers favor closer-to-us and further-from-opponent slightly.
        key = (-1 if margin > 0 else 0, -margin, ds, -do, abs(rx - (w - 1) / 2) + abs(ry - (h - 1) / 2), rx, ry)
        if best_key is None or key < best_key:
            best_key, best = key, (rx, ry)

    tx, ty = best
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    moves = [(dx, dy)]
    # Deterministic fallback move ordering (prefer reducing distance to target, then staying safe).
    pref = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if (dx, dy) not in moves:
        moves = [m for m in pref if m == (dx, dy)] + [m for m in pref if m != (dx, dy)]
    else:
        moves = [m for m in moves] + [m for m in pref if m != (dx, dy)]

    for mx, my in moves:
        nx, ny = sx + mx, sy + my
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            # Ensure we don't step into immediate worse commitment if avoidable: prefer non-increasing target distance.
            if cheb(nx, ny, tx, ty) <= cheb(sx, sy, tx, ty) or (nx, ny) == (ox, oy):
                return [mx, my]

    return [0, 0]