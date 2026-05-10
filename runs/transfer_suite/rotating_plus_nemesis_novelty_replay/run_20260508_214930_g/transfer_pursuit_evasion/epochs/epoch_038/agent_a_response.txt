def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    obs = set()
    for b in obstacles:
        if isinstance(b, (list, tuple)) and len(b) >= 2:
            obs.add((int(b[0]), int(b[1])))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid_moves(x, y):
        mv = []
        for dx, dy in deltas:
            nx, ny = x + dx, y + dy
            if inside(nx, ny) and (nx, ny) not in obs:
                mv.append((dx, dy, nx, ny))
        return mv

    my_moves = valid_moves(sx, sy)
    op_moves = valid_moves(ox, oy)

    # If something unexpected happens, default to staying still.
    if not my_moves or not op_moves:
        return [0, 0]

    best = None  # (utility, dx, dy)
    for mdx, mdy, nx, ny in my_moves:
        worst = None
        for odx, ody, nxo, nyo in op_moves:
            ddx, ddy = nx - nxo, ny - nyo
            dist2 = ddx * ddx + ddy * ddy
            if worst is None or dist2 > worst:
                worst = dist2
        # Tie-breakers: smaller worst distance, then closer current distance, then deterministic move preference.
        cur_dx, cur_dy = sx - ox, sy - oy
        cur_dist2 = cur_dx * cur_dx + cur_dy * cur_dy
        tie = (mdx * 7 + mdy * 3)  # deterministic but arbitrary
        utility = (worst, cur_dist2, tie)
        if best is None or utility < best[0]:
            best = (utility, mdx, mdy)

    return [best[1], best[2]]