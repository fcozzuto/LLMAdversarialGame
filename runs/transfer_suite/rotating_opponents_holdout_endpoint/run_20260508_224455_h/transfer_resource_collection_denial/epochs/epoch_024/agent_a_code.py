def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obs_list)
    if not resources:
        return [0, 0]

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    def pressure(x, y):
        p = 0
        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(1,1),(-1,1),(1,-1),(0,0)]:
            nx, ny = x + dx, y + dy
            if (nx, ny) in obstacles:
                p += 1
        return p

    # Choose best resource by race advantage (deterministic)
    best = None
    second = None
    for rx, ry in resources:
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        key = (sd - od, sd, -pressure(rx, ry), rx, ry)
        if best is None or key < best[0]:
            second = best
            best = (key, (rx, ry))
        elif second is None or key < second[0]:
            second = (key, (rx, ry))

    tx, ty = best[1] if best is not None else resources[0]

    # Greedy step toward target, avoiding obstacles; if stuck, switch to second-best
    def step_towards(tgt):
        rx, ry = tgt
        best_move = (10**9, 10**9, 0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not in_bounds(nx, ny) or (nx, ny) in obstacles:
                continue
            # prefer smaller distance to target, avoid obstacle "pressure" and avoid giving opponent closer access
            d = man(nx, ny, rx, ry)
            opp_d = man(ox, oy, rx, ry)
            key = (d, pressure(nx, ny), -opp_d, dx, dy)
            if key < best_move:
                best_move = key
        if best_move[2:] == (0, 0, 0) or best_move[3:] == (0, 0):
            # might be only invalid moves; fall back to staying
            return [0, 0]
        return [best_move[3], best_move[4]]

    move = step_towards((tx, ty))

    # If move doesn't reduce distance (blocked/bad bottleneck), use second-best target if available
    if move != [0, 0]:
        nx, ny = sx + move[0], sy + move[1]
        if man(nx, ny, tx, ty) >= man(sx, sy, tx, ty) and second is not None:
            move = step_towards(second[1])
    return move