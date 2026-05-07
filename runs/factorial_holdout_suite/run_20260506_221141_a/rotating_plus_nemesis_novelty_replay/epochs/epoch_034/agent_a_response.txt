def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw = int(observation.get("grid_width", 8))
    gh = int(observation.get("grid_height", 8))

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            px, py = int(p[0]), int(p[1])
            if 0 <= px < gw and 0 <= py < gh:
                obs.add((px, py))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < gw and 0 <= ry < gh and (rx, ry) not in obs:
                resources.append((rx, ry))
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

    best = None
    best_key = (-10**18, -10**18, -10**18)
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        gap = od - sd
        # Prefer taking resources we can reach sooner; if tie, shorter and nearer to keeping distance advantage.
        key = (gap, -sd, -abs((rx - sx)) - abs((ry - sy)))
        if key > best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_mkey = (-10**18, -10**18, -10**18)

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < gw and 0 <= ny < gh):
            continue
        if (nx, ny) in obs:
            continue
        sd2 = cheb(nx, ny, tx, ty)
        od2 = cheb(ox, oy, tx, ty)
        gap2 = od2 - sd2

        # local obstacle avoidance: penalize moves that are adjacent to many obstacles
        adj = 0
        for ax, ay in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)):
            cx, cy = nx + ax, ny + ay
            if (cx, cy) in obs:
                adj += 1

        # small bias to continue "resource advantage" and not oscillate wildly
        turn_pen = abs(dx) + abs(dy)

        mkey = (gap2, -sd2, -adj - 0.05 * turn_pen)
        if mkey > best_mkey:
            best_mkey = mkey
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]