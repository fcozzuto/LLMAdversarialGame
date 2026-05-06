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

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    def blocked(nx, ny):
        return (nx, ny) in obstacles

    if not resources:
        dx = 0 if ox == x else (1 if ox > x else -1)
        dy = 0 if oy == y else (1 if oy > y else -1)
        return [-dx, -dy]

    opp_best_res = None
    opp_best_t = 10**9
    for rx, ry in resources:
        t = man(ox, oy, rx, ry)
        if t < opp_best_t:
            opp_best_t = t
            opp_best_res = (rx, ry)

    best_move = (0, 0)
    best_val = -10**18

    for mdx, mdy in dirs:
        nx, ny = x + mdx, y + mdy
        if not in_bounds(nx, ny) or blocked(nx, ny):
            continue

        val = 0
        for rx, ry in resources:
            ts = man(nx, ny, rx, ry)
            to = man(ox, oy, rx, ry)
            if ts <= to:
                val += 200 - 10 * ts + (to - ts) * 15
            else:
                val -= 20 + 2 * ts - 3 * to

        # Pressure/denial: reduce opponent's access to its closest resource
        if opp_best_res is not None:
            brx, bry = opp_best_res
            before = man(ox, oy, brx, bry)
            after = man(ox, oy, brx, bry)  # ours doesn't change opponent directly, but diagonal/positioning changes who can intercept
            # Use our proximity as a proxy for denial: move to states that would let us contest quickly
            val += max(0, 30 - man(nx, ny, brx, bry)) - 2 * man(nx, ny, ox, oy)

        # Deterministic tie-break: prefer staying closer to center-ish (minimax on deviation)
        center_pen = abs((w - 1) / 2 - nx) + abs((h - 1) / 2 - ny)
        val -= center_pen * 0.01

        if val > best_val:
            best_val = val
            best_move = (mdx, mdy)

    return [best_move[0], best_move[1]]