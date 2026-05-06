def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0)) or (0, 0)
    ox, oy = observation.get("opponent_position", (0, 0)) or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles", []) or []
    obs_set = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs_set.add((x, y))

    resources = observation.get("resources", []) or []
    res_list = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs_set:
                res_list.append((x, y))
    if not res_list:
        return [0, 0]

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    def risk(x, y):
        rr = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx or dy:
                    if (x + dx, y + dy) in obs_set:
                        rr += 1
        return rr

    # Pick best target: prefer being closer than opponent, avoid high-risk squares.
    best_t = None
    best_v = -10**9
    for cx, cy in res_list:
        sd = man(sx, sy, cx, cy)
        od = man(ox, oy, cx, cy)
        lead = od - sd  # positive => we are closer (good)
        v = 3 * lead - sd - 2 * (sd > 0 and lead < 0) - 5 * risk(cx, cy)
        if (cx == sx and cy == sy):
            v += 1000
        if v > best_v:
            best_v = v
            best_t = (cx, cy)

    tx, ty = best_t
    # Choose move delta; if blocked toward target, try all deltas deterministically by score.
    deltas = [(-1, -1), (0, -1), (1, -1),
              (-1, 0), (0, 0), (1, 0),
              (-1, 1), (0, 1), (1, 1)]

    best_move = (0, 0)
    best_score = -10**9

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs_set:
            continue
        d_to_target = man(nx, ny, tx, ty)
        d_opp = man(ox, oy, tx, ty)
        # Move should improve our advantage for the target; also reduce risk near us.
        score = 6 * (d_opp - d_to_target) - d_to_target - 2 * risk(nx, ny)
        if (nx, ny) == (tx, ty):
            score += 800
        # Deterministic tie-break preference: smaller dx, then smaller dy.
        if score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]