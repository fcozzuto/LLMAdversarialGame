def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = map(int, observation.get("self_position", [0, 0]))
    ox, oy = map(int, observation.get("opponent_position", [0, 0]))

    obs = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    dirs = [(-1, -1), (0, -1), (1, -1),
            (-1, 0), (0, 0), (1, 0),
            (-1, 1), (0, 1), (1, 1)]

    if resources:
        # Pick best contested target: prioritize where opponent is farther from it than we are.
        best_t = None
        best_score = None
        for rx, ry in resources:
            sd = cheb(sx, sy, rx, ry)
            od = cheb(ox, oy, rx, ry)
            # Primary: (od - sd). Secondary: smaller sd. Tertiary: sum coords for determinism.
            score = (od - sd, -sd, -(rx + ry))
            if best_score is None or score > best_score:
                best_score = score
                best_t = (rx, ry)
        tx, ty = best_t
    else:
        # No visible resources: drift toward center.
        tx, ty = w // 2, h // 2

    opp_dist = cheb(ox, oy, tx, ty)

    best_move = [0, 0]
    best_val = None
    # Deterministic tie-break: fixed order in dirs.
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        nd = cheb(nx, ny, tx, ty)
        # Value favors becoming closer to target than opponent, and reduces distance to target.
        lead = opp_dist - nd
        val = lead * 3 - nd
        # Small deterrent from moving away from the best target if we don't improve.
        if nd > cheb(sx, sy, tx, ty):
            val -= 1
        if best_val is None or val > best_val:
            best_val = val
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]