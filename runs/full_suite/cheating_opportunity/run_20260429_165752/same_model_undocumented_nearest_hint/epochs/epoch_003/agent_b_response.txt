def choose_move(observation):
    W = observation["grid_width"]; H = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []) if p and len(p) >= 2)

    def inside(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2; dx = -dx if dx < 0 else dx
        dy = y1 - y2; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inside(nx, ny):
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    valid_res = [(x, y) for x, y in resources if (x, y) not in obstacles]
    if not valid_res:
        cx, cy = W // 2, H // 2
        best = None
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            d = cheb(nx, ny, cx, cy)
            if best is None or d < best[0]:
                best = (d, dx, dy)
        return [best[1], best[2]]

    # Contest the resource the opponent is closest to (shifts strategy from greedy chase to interception).
    opp_target = None
    best_od = None
    for rx, ry in valid_res:
        d = cheb(ox, oy, rx, ry)
        if best_od is None or d < best_od or (d == best_od and (rx < opp_target[0] if opp_target else True)):
            best_od = d
            opp_target = (rx, ry)

    tx, ty = opp_target
    # If we're far from target, also consider a secondary target nearer to us to avoid getting stuck.
    min_self = None
    sec = None
    for rx, ry in valid_res:
        d = cheb(sx, sy, rx, ry)
        if min_self is None or d < min_self:
            min_self = d; sec = (rx, ry)
    sx2, sy2 = sec

    # Score move: maximize (opponent distance after move to target - our distance after move to target)
    # while lightly preferring shorter paths to the secondary target.
    best_score = None
    best_move = (0, 0)
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        d_self_t = cheb(nx, ny, tx, ty)
        d_opp_t_after = best_od  # opponent doesn't move in this simulation; use current to stay deterministic/stable
        contest = d_opp_t_after - d_self_t

        d_self_sec = cheb(nx, ny, sx2, sy2)
        # Small tie-breakers: prefer moves that also reduce our distance to opponent (pressure) and toward target.
        pressure = cheb(nx, ny, ox, oy)
        dist_to_tx = d_self_t

        score = contest * 10 - d_self_sec - pressure * 0.05 - dist_to_tx * 0.01
        if best_score is None or score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]