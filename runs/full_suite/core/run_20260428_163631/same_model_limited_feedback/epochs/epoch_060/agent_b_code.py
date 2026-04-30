def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set(tuple(p) for p in observation["obstacles"])

    deltas = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def sd(p, q):
        dx = p[0]-q[0]; dy = p[1]-q[1]
        return dx*dx + dy*dy

    # Choose a resource where we are relatively advantaged vs opponent
    best_res = None
    best_adv = -10**18
    if resources:
        for r in resources:
            adv = sd((sx, sy), r) * -1  # higher is better
            oppd = sd((ox, oy), r)
            adv += oppd  # maximize (opp_dist - self_dist) in squared distance
            if adv > best_adv:
                best_adv = adv
                best_res = r

    # If no resources, just head to center-ish to keep flexibility
    if best_res is None:
        target = (w//2, h//2)
    else:
        target = best_res

    # Opponent proximity to same target for mild blocking pressure
    opp_same_pressure = 0
    if resources:
        opp_best = None
        opp_best_d = None
        for r in resources:
            d = sd((ox, oy), r)
            if opp_best_d is None or d < opp_best_d:
                opp_best_d = d; opp_best = r
        if opp_best == target:
            opp_same_pressure = 1

    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny): 
            continue
        if (nx, ny) in obstacles:
            score = -10**12
        else:
            d_to_target = sd((nx, ny), target)
            # Encourage reaching target, avoid giving opponent an easy approach to us/target
            d_opp = sd((nx, ny), (ox, oy))
            score = -d_to_target + 0.02 * d_opp
            if opp_same_pressure:
                # When we contest, try to keep some distance from opponent while closing on target
                score += 0.01 * d_opp
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]