def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obs = set(tuple(p) for p in observation.get("obstacles", []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = abs(ax - bx)
        dy = abs(ay - by)
        return dx if dx > dy else dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        return [0, 0]

    best_target = None
    best_key = None
    for rx, ry in resources:
        d_self = cheb(sx, sy, rx, ry)
        d_opp = cheb(ox, oy, rx, ry)
        if d_opp <= 1:
            continue
        # Prefer big advantage; tie-break for closer to us
        key = (d_opp - d_self, -d_self, -rx, -ry)
        if best_key is None or key > best_key:
            best_key = key
            best_target = (rx, ry)
    if best_target is None:
        best_target = min(resources, key=lambda r: cheb(sx, sy, r[0], r[1]))

    rx, ry = best_target
    cur_dist_self = cheb(sx, sy, rx, ry)
    cur_dist_opp = cheb(ox, oy, rx, ry)

    best_move = (0, 0)
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            # Engine would keep us in place; still allow as deterministic fallback
            nx, ny = sx, sy
            dx, dy = 0, 0

        d_self = cheb(nx, ny, rx, ry)
        d_opp = cheb(ox, oy, rx, ry)  # opponent doesn't move this turn
        adv = d_opp - d_self

        # Discourage stepping into positions that hand the opponent the same cell/resource soon
        threat = 0
        for tx, ty in resources:
            if (tx, ty) == (rx, ry):
                continue
            if cheb(nx, ny, tx, ty) == 0 and cheb(ox, oy, tx, ty) <= 2:
                threat += 10
            if cheb(ox, oy, tx, ty) <= 1:
                threat += 1

        # Primary: maximize advantage; Secondary: minimize distance to our target
        val = (adv, -d_self, -((abs(nx - ox) + abs(ny - oy)) // 1), -threat)
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    # If we didn't improve at all, try a slight detour toward the most available resource
    if best_val is not None and best_move == (0, 0) and cur_dist_self <= 1:
        # near target; just move to reduce distance to opponent less relevant
        best_cell = min(resources, key=lambda r: (cheb(ox, oy, r[0], r[1]) <= 2, cheb(sx, sy, r[0], r[1])))
        tx, ty = best_cell
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        return [dx, dy]

    return [int(best_move[0]), int(best_move[1])]