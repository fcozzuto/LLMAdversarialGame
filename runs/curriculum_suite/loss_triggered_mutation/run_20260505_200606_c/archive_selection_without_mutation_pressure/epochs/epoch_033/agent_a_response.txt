def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", [])
    if not resources:
        return [0, 0]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def dist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy  # Chebyshev (diagonal cost)
    
    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    # Precompute opponent urgency to resources
    opp_to = []
    for rx, ry in resources:
        opp_to.append(dist(ox, oy, rx, ry))
    opp_urgency = min(opp_to)

    best_move = (0, 0)
    best_val = -10**18
    tie = 0
    pref = [(-1, 0), (0, -1), (1, 0), (0, 1), (0, 0), (-1, -1), (1, -1), (-1, 1), (1, 1)]

    for dx, dy in pref:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        # Our best approach distance and interception pressure
        our_best = 10**9
        best_res_val = -10**18
        for (rx, ry) in resources:
            our_d = dist(nx, ny, rx, ry)
            if our_d < our_best:
                our_best = our_d
            opp_d = dist(ox, oy, rx, ry)
            lead = opp_d - our_d  # positive means we are closer
            val = lead * 10
            if opp_d <= 4 and our_d <= opp_d:
                val += 12  # prioritize stealing close resources
            if our_d == our_best:
                val += 2
            best_res_val = val if val > best_res_val else best_res_val

        # Also discourage moves that let opponent be too safe (urgency)
        our_urgency = our_best
        safety = (opp_urgency - our_urgency) * 3  # higher if we reduce its best pace
        total = best_res_val + safety - (1 if (nx, ny) == (sx, sy) else 0) * 1

        if total > best_val:
            best_val = total
            best_move = (dx, dy)
            tie = 0

    return [best_move[0], best_move[1]]