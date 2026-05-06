def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    x, y = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])
    obs = set((a, b) for a, b in obstacles)
    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    def cheb(ax, ay, bx, by):
        dx = ax - bx; dx = -dx if dx < 0 else dx
        dy = ay - by; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy

    if not resources:
        tx, ty = w - 1, h - 1
        bx, by = 0, 0
        best = [0, 0]; bestv = -10**18
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if not valid(nx, ny): 
                continue
            v = cheb(nx, ny, ox, oy) * 300 - (abs(nx - tx) + abs(ny - ty)) * 2 - cheb(nx, ny, bx, by)
            if v > bestv:
                bestv = v; best = [dx, dy]
        return best

    # Evaluate immediate move by its effect on our lead over best attainable resource,
    # plus a small term for not letting the opponent get closer to their best resource.
    best_move = [0, 0]; best_val = -10**18
    opp_best = -10**18
    for rx, ry in resources:
        opp_best = max(opp_best, cheb(ox, oy, rx, ry))
    # opp_best is max; we mainly need per-resource values below

    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not valid(nx, ny):
            continue

        # Find resource where our move creates the largest advantage.
        best_adv = -10**18
        best_sec_dist = 10**18
        opp_best_dist = 10**18
        for rx, ry in resources:
            d_ours = cheb(nx, ny, rx, ry)
            d_opp = cheb(ox, oy, rx, ry)
            adv = d_opp - d_ours  # positive means we are closer to that resource
            if adv > best_adv or (adv == best_adv and d_ours < best_sec_dist):
                best_adv = adv
                best_sec_dist = d_ours
                opp_best_dist = d_opp

        # If resources are all risky (adv negative), still choose move that makes
        # us least-worse and indirectly pressures the opponent's next pick.
        # Opponent pressure term: reduce their distance to the resource they are likely to take.
        # Approx: consider the single resource that minimizes opponent distance.
        opp_target_dist = 10**18
        for rx, ry in resources:
            opp_target_dist = min(opp_target_dist, cheb(ox, oy, rx, ry))

        # Small safety: prefer staying away from obstacles already handled by validity,
        # and slightly prefer moving toward the best-adv resource.
        toward_term = -best_sec_dist
        opp_press = -(opp_target_dist - 0.1 * opp_best_dist) * 0.05

        val = best_adv * 120 + toward_term * 2 + opp_press
        if val > best_val:
            best_val = val; best_move = [dx, dy]

    return best_move