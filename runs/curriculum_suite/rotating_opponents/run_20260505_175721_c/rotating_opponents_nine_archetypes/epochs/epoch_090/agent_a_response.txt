def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0)) or (0, 0)
    ox, oy = observation.get("opponent_position", (0, 0)) or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
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

    def legal_moves(x, y):
        res = []
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                    res.append((dx, dy, nx, ny))
        return res

    self_moves = legal_moves(sx, sy)

    best_target = resources[0]
    best_val = -10**18
    for tx, ty in resources:
        ds = cheb(sx, sy, tx, ty)
        do = cheb(ox, oy, tx, ty)
        # Prefer resources where we are closer; also prefer those with fewer cells for opponent to "steal".
        # Tie-break deterministically toward higher y then x to avoid oscillation.
        val = (do - ds) * 1000 + (0 - do) * 10 - (abs(tx - 3.5) + abs(ty - 3.5))
        if val > best_val or (val == best_val and (ty, tx) > (best_target[1], best_target[0])):
            best_val = val
            best_target = (tx, ty)

    tx, ty = best_target
    desired_dx = 0 if tx == sx else (1 if tx > sx else -1)
    desired_dy = 0 if ty == sy else (1 if ty > sy else -1)

    # Evaluate legal moves toward target, but if opponent is significantly closer, briefly favor moves that
    # increase distance to opponent (to avoid simultaneous contest near the same resource).
    contest = cheb(ox, oy, tx, ty) - cheb(sx, sy, tx, ty)
    favor_opp_avoid = contest >= 2

    best = (0, 0, -10**18)
    for dx, dy, nx, ny in self_moves:
        ds2 = cheb(nx, ny, tx, ty)
        opp_d2 = cheb(nx, ny, ox, oy)
        # Small penalty for deviating from desired direction to keep forward progress.
        dev = abs(desired_dx - dx) + abs(desired_dy - dy)
        val = -ds2 * 100 - dev * 3
        if favor_opp_avoid:
            val += opp_d2 * 2
        if val > best[2]:
            best = (dx, dy, val)

    return [int(best[0]), int(best[1])]