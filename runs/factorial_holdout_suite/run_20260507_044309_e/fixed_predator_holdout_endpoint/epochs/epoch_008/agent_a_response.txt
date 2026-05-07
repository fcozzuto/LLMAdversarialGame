def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set((x, y) for x, y in (observation.get("obstacles", []) or []))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    cand = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inside(nx, ny) and (nx, ny) not in obstacles:
                cand.append((dx, dy, nx, ny))
    if not cand:
        return [0, 0]

    if not resources:
        # Move toward midpoint between agents to keep access to resources
        mx, my = (sx + ox) // 2, (sy + oy) // 2
        best = None
        bestv = None
        for dx, dy, nx, ny in cand:
            v = -((nx - mx) * (nx - mx) + (ny - my) * (ny - my)) - 0.1 * (abs(nx - ox) + abs(ny - oy))
            if bestv is None or v > bestv:
                bestv = v
                best = [dx, dy]
        return best if best is not None else [0, 0]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Pick a target resource we can plausibly reach before the opponent
    best_r = None
    best_score = None
    for rx, ry in resources:
        ds = man(sx, sy, rx, ry)
        do = man(ox, oy, rx, ry)
        # Advantage: how much closer we are than opponent; tie-break by absolute closeness
        adv = do - ds
        sec = -ds
        # Prefer resources that are not essentially "in opponent's reach" while we are far
        reach_block = 0
        if do <= 2 and ds > 2:
            reach_block = -1000
        score = (adv * 100 - ds) + reach_block + sec * 0.01
        if best_score is None or score > best_score:
            best_score = score
            best_r = (rx, ry)

    tx, ty = best_r

    # Choose the move that best reduces distance to target while not rushing into opponent
    best = None
    bestv = None
    for dx, dy, nx, ny in cand:
        d_now = man(nx, ny, tx, ty)
        d_tar = man(sx, sy, tx, ty)
        # If already at target, stay put would be rejected by engine only if invalid; still allow [0,0] if possible
        progress = d_tar - d_now
        opp_close = man(nx, ny, ox, oy)
        opp_pen = -3.0 * (max(0, 4 - opp_close))  # avoid giving immediate denial/contest
        block_pen = 0
        # Small penalty if move increases distance to target but opponent is very close to it
        do = man(ox, oy, tx, ty)
        if do <= 2 and progress < 0:
            block_pen = -2.0
        v = progress * 10 + opp_pen + block_pen - 0.01 * (d_now * d_now)
        if bestv is None or v > bestv:
            bestv = v
            best = [dx, dy]

    return best if best is not None else [0, 0]