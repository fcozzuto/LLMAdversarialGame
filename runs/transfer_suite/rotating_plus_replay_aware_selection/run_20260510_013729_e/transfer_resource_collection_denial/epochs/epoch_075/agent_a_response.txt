def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    if not resources:
        return [0, 0]

    obst = {(x, y) for x, y in obstacles}
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        if dx < 0:
            dx = -dx
        if dy < 0:
            dy = -dy
        return dx + dy

    # One-step lookahead: choose move maximizing (opponent lead) at our next position,
    # plus a small obstacle-avoidance term and a "reachability" tie-break.
    best_dx, best_dy = 0, 0
    best_val = -10**18
    best_reach = 10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obst:
            continue

        # local obstacle penalty (discourage getting adjacent to obstacles)
        pn = 0
        for ex, ey in obstacles:
            if abs(ex - nx) <= 1 and abs(ey - ny) <= 1:
                pn += 1

        # evaluate best resource for us after this move
        val = -10**18
        reach = 10**18
        for rx, ry in resources:
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            # Prefer resources where we are closer than opponent (od - sd large),
            # and within that, prefer shorter self distance (reach).
            v = (od - sd) * 1000 - sd - pn * 5
            if v > val or (v == val and sd < reach):
                val = v
                reach = sd

        if val > best_val or (val == best_val and reach < best_reach):
            best_val = val
            best_reach = reach
            best_dx, best_dy = dx, dy

    return [best_dx, best_dy]