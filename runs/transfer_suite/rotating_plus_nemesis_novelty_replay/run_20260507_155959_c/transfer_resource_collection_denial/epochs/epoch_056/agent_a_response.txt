def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if inb(x, y): obs.add((x, y))
    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if inb(x, y) and (x, y) not in obs: res.append((x, y))
    if (sx, sy) in obs: return [0, 0]
    if not res: return [0, 0]

    # Predict opponent's next move: head to their nearest remaining resource.
    def md(ax, ay, bx, by): 
        d1 = ax - bx; d2 = ay - by
        return (d1 if d1 >= 0 else -d1) + (d2 if d2 >= 0 else -d2)
    target = None; bestd = 10**9
    for rx, ry in res:
        d = md(ox, oy, rx, ry)
        if d < bestd:
            bestd = d; target = (rx, ry)
    tx, ty = target
    stepx = 0 if tx == ox else (1 if tx > ox else -1)
    stepy = 0 if ty == oy else (1 if ty > oy else -1)
    pred_next = (ox + stepx, oy + stepy)
    if not inb(pred_next[0], pred_next[1]) or pred_next in obs:
        pred_next = (ox, oy)

    # Intercept: choose our move that minimizes distance to predicted opponent next cell,
    # while prioritizing landing on a resource.
    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    resource_set = set(res)
    best_move = (0, 0); best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs: 
            continue
        dist_to_pred = md(nx, ny, pred_next[0], pred_next[1])
        on_res = (nx, ny) in resource_set
        dist_to_target = md(nx, ny, tx, ty)
        # Primary: interception; Secondary: don't drift far from target line
        score = (-dist_to_pred) * 10 - dist_to_target
        if on_res:
            score += 10**6
        if score > best_score:
            best_score = score; best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]