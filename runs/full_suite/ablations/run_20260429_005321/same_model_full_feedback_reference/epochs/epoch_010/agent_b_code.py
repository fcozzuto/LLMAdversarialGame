def choose_move(observation):
    w = int(observation["grid_width"]); h = int(observation["grid_height"])
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    res = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))

    def md(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    me = (sx, sy); opp = (ox, oy)
    if res:
        tgt = min(res, key=lambda r: (md(me, r), -md(opp, r)))
    else:
        corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
        tgt = max(corners, key=lambda c: md(opp, c))

    tx, ty = tgt
    stepx = 0 if tx == sx else (1 if tx > sx else -1)
    stepy = 0 if ty == sy else (1 if ty > sy else -1)

    # Prefer moving toward target, then toward blocking opponent, avoid obstacles/out-of-bounds.
    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        dist_to = abs(nx - tx) + abs(ny - ty)
        dist_opp_to = abs(nx - ox) + abs(ny - oy)
        score = -dist_to + 0.1 * dist_opp_to
        if dx == stepx and dy == stepy:
            score += 2.0
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]