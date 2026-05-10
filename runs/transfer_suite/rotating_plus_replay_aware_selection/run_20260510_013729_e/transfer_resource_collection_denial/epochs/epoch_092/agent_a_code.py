def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    if not resources:
        return [0, 0]
    obst = {(x, y) for x, y in obstacles}

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def legal(x, y):
        return inb(x, y) and (x, y) not in obst

    def dist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    opp_nearest = None
    best_opp_d = 10**9
    for rx, ry in resources:
        d = dist(ox, oy, rx, ry)
        if d < best_opp_d:
            best_opp_d = d
            opp_nearest = (rx, ry)

    best = None
    best_key = None
    for rx, ry in resources:
        sd = dist(sx, sy, rx, ry)
        od = dist(ox, oy, rx, ry)
        # Prefer beating opponent; also prefer smaller self distance as tie-break.
        key = (od - sd, -sd, -abs(rx - ox) - abs(ry - oy))
        if opp_nearest == (rx, ry):
            # If opponent is already targeting this resource, try to deny by switching.
            key = (key[0] - 2, key[1] - 1, key[2])
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best

    # Greedy step toward target with obstacle avoidance; deterministic tie-break order by moves list.
    bestx, besty, bestd = sx, sy, 10**9
    for mdx, mdy in moves:
        nx, ny = sx + mdx, sy + mdy
        if not legal(nx, ny):
            continue
        d = dist(nx, ny, tx, ty)
        if d < bestd:
            bestd = d
            bestx, besty = nx, ny

    return [bestx - sx, besty - sy]