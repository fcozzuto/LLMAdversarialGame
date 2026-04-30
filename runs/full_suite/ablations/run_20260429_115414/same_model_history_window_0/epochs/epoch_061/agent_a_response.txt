def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set(tuple(p) for p in observation["obstacles"])
    sname = observation.get("self_name", "a")
    # Neighbors including stay
    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h
    def d2(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return dx*dx + dy*dy
    # Select resource to pursue: minimize (self_dist - opp_dist), alternate preference by turn
    turn = observation.get("turn_index", 0)
    best = None
    for r in resources:
        rx, ry = r
        if (rx, ry) in obstacles:
            continue
        sd = d2((sx, sy), (rx, ry))
        od = d2((ox, oy), (rx, ry))
        score = (sd - od, sd, rx, ry)
        # Small deterministic perturbation to vary behavior
        if (turn + rx + ry) % 2 == (0 if sname else 0):
            score = (score[0]*1.0 - 0.001, score[1], score[2], score[3])
        if best is None or score < best[0]:
            best = (score, (rx, ry))
    if best is None:
        # No resources visible: drift to center-ish while avoiding obstacles and opponent
        tx, ty = (w//2, h//2)
    else:
        tx, ty = best[1]
    # If opponent is extremely close to a resource we can contest, bias towards intercept near them
    close_opp = d2((sx, sy), (ox, oy)) <= 4
    # Evaluate candidate moves
    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        # Distance to target
        val = d2((nx, ny), (tx, ty))
        # Slightly prefer staying away from opponent when contesting
        if close_opp:
            val += 0.5 * d2((nx, ny), (ox, oy))
        # If move would reduce opponent's access more than ours, allow
        # Use opposite bias when opponent is closer to target
        if best is not None:
            od = d2((ox, oy), (tx, ty))
            sd = d2((sx, sy), (tx, ty))
            if od < sd:
                val -= 0.25 * (d2((ox, oy), (tx, ty)) - d2((nx, ny), (tx, ty)))
        # Deterministic tie-break: lexicographic by move
        tie = (val, abs(dx) + abs(dy), dx, dy)
        if best_val is None or tie < best_val:
            best_val = tie
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]