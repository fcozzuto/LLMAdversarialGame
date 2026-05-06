def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def in_bounds(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def sign(v):
        return 0 if v == 0 else (1 if v > 0 else -1)

    def dist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    def cell_blocked(nx, ny):
        return (nx, ny) in obstacles

    if not resources:
        return [-sign(ox - x), -sign(oy - y)]

    # Only consider the top few closest resources to reduce noise and stay deterministic/fast.
    res_sorted = sorted(resources, key=lambda r: dist(x, y, r[0], r[1]))
    res_sorted = res_sorted[:6]

    best = (0, 0)
    best_sc = None

    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not in_bounds(nx, ny) or cell_blocked(nx, ny):
            continue

        self_to_opp = dist(nx, ny, ox, oy)
        sc = 0.0
        # Encourage taking resources before opponent, but also keep pressure via opponent distance.
        for rx, ry in res_sorted:
            dS = dist(nx, ny, rx, ry)
            dO = dist(ox, oy, rx, ry)
            margin = dO - dS  # positive if we are closer now than opponent
            if margin > 0:
                sc += 6.0 + 2.0 * margin - 0.15 * dS
            else:
                sc += -0.6 - 0.25 * (-margin) - 0.10 * dS
        # If we can "block" opponent pressure by moving closer to it while still scoring, do so.
        sc += 0.08 * (12 - self_to_opp)

        # Tie-break deterministically: prefer staying closer to resources, then smaller dx,dy order.
        if best_sc is None or sc > best_sc:
            best_sc = sc
            best = (dx, dy)
        elif sc == best_sc:
            if dist(nx, ny, res_sorted[0][0], res_sorted[0][1]) < dist(x + best[0], y + best[1], res_sorted[0][0], res_sorted[0][1]):
                best = (dx, dy)

    return [best[0], best[1]]