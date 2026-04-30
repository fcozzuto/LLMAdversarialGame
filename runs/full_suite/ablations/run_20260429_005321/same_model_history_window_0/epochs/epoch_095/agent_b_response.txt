def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation["resources"]; obstacles = set(tuple(p) for p in observation["obstacles"])
    if not resources:
        return [0, 0]
    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    def cheb(a,b,c,d): 
        x=a-c; y=b-d
        return abs(x) if abs(x)>=abs(y) else abs(y)
    # Pick target: prefer resources where we are closer than opponent; otherwise closer to any.
    best = None
    for rx, ry in resources:
        if (rx, ry) in obstacles: 
            continue
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        lead = do - ds
        # Small bias toward bottom-right diagonal progress (matches typical opposite-corner start patterns).
        bias = (rx - sx) * 0.001 + (ry - sy) * 0.001
        score = (lead * 10.0) + (-ds) + bias
        if best is None or score > best[0]:
            best = (score, rx, ry)
    _, tx, ty = best
    # Evaluate moves by resulting distance to target; avoid obstacles; tie-break toward blocking/opponent.
    opp_d = cheb(ox, oy, tx, ty)
    best_move = (0, 0); best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h: 
            continue
        if (nx, ny) in obstacles:
            continue
        nd = cheb(nx, ny, tx, ty)
        # Blocking heuristic: if we can get to a cell where opponent would be closer next.
        nd_opp = cheb(ox, oy, tx, ty)
        # If we move to reduce our distance while not worsening opponent's relative pressure much.
        val = (-nd * 2.0) + (opp_d - nd_opp) + (1.5 if (nx, ny) == (tx, ty) else 0.0)
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]