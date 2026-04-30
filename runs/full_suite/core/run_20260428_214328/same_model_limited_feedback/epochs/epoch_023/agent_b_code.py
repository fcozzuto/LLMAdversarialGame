def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation["resources"]; obstacles = observation["obstacles"]
    obs_set = {(a[0], a[1]) for a in obstacles}
    def clamp(x, y):
        if x < 0: x = 0
        elif x >= w: x = w - 1
        if y < 0: y = 0
        elif y >= h: y = h - 1
        return x, y
    def dist(a, b):
        dx = abs(a[0] - b[0]); dy = abs(a[1] - b[1])
        return dx if dx > dy else dy  # chebyshev
    opp_d = dist((sx, sy), (ox, oy))
    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    # Target selection: pick resource where we are more likely to arrive first.
    best_res = None; best_key = None
    if resources:
        for r in resources:
            rd = dist((sx, sy), r)
            od = dist((ox, oy), r)
            adv = od - rd  # positive means we're closer
            key = (adv, -rd, - (r[0]+r[1]))  # deterministic tie-break
            if best_key is None or key > best_key:
                best_key = key; best_res = r
    else:
        best_res = (sx, sy)
    # Obstacle-avoidance: prefer positions that reduce local collision risk.
    # Also adapt since last epoch was worse: be more defensive if opponent is close.
    defend = opp_d <= 2
    best_move = (0, 0); best_score = -10**9
    for dx, dy in moves:
        nx, ny = clamp(sx + dx, sy + dy)
        if (nx, ny) in obs_set:
            continue
        nd_self = dist((nx, ny), best_res)
        nd_opp = dist((nx, ny), (ox, oy))
        # If defending, don't rush; increase separation.
        sep_bonus = nd_opp - opp_d
        # Encourage getting closer to chosen resource, but avoid trapping near obstacles.
        local_block = 0
        for tx, ty in [(nx+1,ny),(nx-1,ny),(nx,ny+1),(nx,ny-1)]:
            tx, ty = clamp(tx, ty)
            if (tx, ty) in obs_set:
                local_block += 1
        res_score = -nd_self
        if defend:
            score = 2.0*sep_bonus + 0.3*res_score - 0.6*local_block
        else:
            score = 1.2*sep_bonus + 0.9*res_score - 0.6*local_block
        # If we already reached resource position, stay favorable.
        if (nx, ny) in {(r[0], r[1]) for r in resources}:
            score += 5.0
        if score > best_score:
            best_score = score; best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]