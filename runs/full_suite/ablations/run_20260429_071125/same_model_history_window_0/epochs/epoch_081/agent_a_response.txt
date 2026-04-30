def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set(tuple(p) for p in observation["obstacles"])
    deltas = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    inside = lambda x, y: 0 <= x < w and 0 <= y < h
    man = lambda x1, y1, x2, y2: abs(x1 - x2) + abs(y1 - y2)
    pref_far = (observation["turn_index"] % 2 == 1)
    best_res = None
    best_val = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        ds = man(sx, sy, rx, ry)
        do = man(ox, oy, rx, ry)
        ahead_bias = 4 if do <= ds else 0
        # minimize target value; prefer closer when pref_far is False, else prefer farther
        val = (ds if not pref_far else -ds) + 0.6 * (do - ds) + ahead_bias * 10
        if best_val is None or val < best_val or (val == best_val and (rx+ry) < (best_res[0]+best_res[1])):
            best_val = val
            best_res = (rx, ry)
    if best_res is None:
        # No accessible resources; move to maximize distance from opponent
        tx, ty = ox, oy
    else:
        tx, ty = best_res
    best_move = [0, 0]
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue
        if best_res is None:
            score = -(man(nx, ny, tx, ty))
        else:
            # Prefer reducing distance to target; avoid giving opponent a short route
            own = man(nx, ny, tx, ty)
            opp = man(ox, oy, tx, ty)
            opp_next = man(ox, oy, tx, ty)  # opponent move unknown; use current pressure estimate
            # discourage moves that significantly worsen own progress while opponent is already competitive
            pressure = 1 if opp <= man(sx, sy, tx, ty) else 0
            score = own + 0.8 * pressure + 0.2 * man(nx, ny, ox, oy)
        if best_score is None or score < best_score:
            best_score = score
            best_move = [dx, dy]
    return best_move