def choose_move(observation):
    sx, sy = observation["self_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = bx - ax
        if dx < 0: dx = -dx
        dy = by - ay
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def obstacle_pen(x, y):
        # small deterministic safety shaping
        d = 10
        for ox, oy in obs:
            dd = cheb(x, y, ox, oy)
            if dd < d:
                d = dd
        if d >= 3:
            return 0
        return (3 - d)

    # Target selection: prefer resources we can reach earlier than opponent (opponent assumed denier by urgency)
    best_r = resources[0]
    best_val = -10**9
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        # opponent position not needed by schema? it exists but not listed in prompt; use only documented:
        # opponent_position is documented
        ox, oy = observation["opponent_position"]
        do = cheb(ox, oy, rx, ry)
        margin = do - ds  # positive means we're earlier
        val = margin * 12 - ds * 2 - obstacle_pen(rx, ry) * 3
        if val > best_val:
            best_val = val
            best_r = (rx, ry)

    rx, ry = best_r
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    cur_ds = cheb(sx, sy, rx, ry)
    best_move = (0, 0)
    best_score = -10**9
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            nx, ny = sx, sy
        nds = cheb(nx, ny, rx, ry)
        if nds > cur_ds + 1:
            continue
        # second preference: avoid moves that let opponent potentially contest sooner by pushing ourselves toward nearer-but-riskier tiles
        ox, oy = observation["opponent_position"]
        do_after = cheb(ox, oy, rx, ry)
        # approximate "contest" by comparing our new arrival distance
        val = (do_after - nds) * 10 - nds * 3 - obstacle_pen(nx, ny) * 2
        if val > best_score:
            best_score = val
            best_move = (dx, dy)

    dx, dy = best_move
    return [int(dx), int(dy)]