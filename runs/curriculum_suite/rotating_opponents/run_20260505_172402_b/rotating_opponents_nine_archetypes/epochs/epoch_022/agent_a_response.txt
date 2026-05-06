def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def cheb(ax, ay, bx, by):
        dx = bx - ax
        if dx < 0: dx = -dx
        dy = by - ay
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = (0, 0)
    best_val = -10**9

    if not resources:
        return [0, 0]

    # Precompute nearest obstacle distance for mild safety shaping
    def obstacle_penalty(x, y):
        # returns integer penalty; 0 if no nearby obstacle
        d = 10
        for (ox2, oy2) in obs:
            dd = cheb(x, y, ox2, oy2)
            if dd < d:
                d = dd
        if d >= 3:
            return 0
        return (3 - d) * 3

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            nx, ny = sx, sy

        my_best = 10**9
        opp_best = 10**9
        for rx, ry in resources:
            d_my = cheb(nx, ny, rx, ry)
            if d_my < my_best:
                my_best = d_my
            d_opp = cheb(ox, oy, rx, ry)
            if d_opp < opp_best:
                opp_best = d_opp

        # Value: create advantage on closest contested resource; bias toward reducing our distance more than theirs
        # Add small preference for moving toward our nearest resource and away from opponent.
        val = (opp_best - my_best) * 100 - my_best * 7 + cheb(ox, oy, nx, ny) * -2
        val -= obstacle_penalty(nx, ny)

        # Additional deterministic bias to break ties: slightly prefer progressing toward center
        cx, cy = w // 2, h // 2
        val -= cheb(nx, ny, cx, cy)

        if val > best_val:
            best_val = val
            best = (dx, dy)

    return [int(best[0]), int(best[1])]