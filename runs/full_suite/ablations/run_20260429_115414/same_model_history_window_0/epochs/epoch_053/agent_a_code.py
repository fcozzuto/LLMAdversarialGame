def choose_move(observation):
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation["obstacles"]
    obs = set((p[0], p[1]) for p in obstacles)
    resources = observation["resources"]

    w, h = observation["grid_width"], observation["grid_height"]

    def cheb(a, b, c, d):
        dx = a - c
        dy = b - d
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    deltas = [[0, 0], [1, 0], [0, 1], [-1, 0], [0, -1], [1, 1], [1, -1], [-1, 1], [-1, -1]]
    best = None
    best_score = -10**18

    if not resources:
        # Fallback: head toward opponent to limit their mobility/claims
        tx, ty = ox, oy
        for dx, dy in deltas:
            nx, ny = x + dx, y + dy
            if nx < 0 or ny < 0 or nx >= w or ny >= h or (nx, ny) in obs:
                continue
            d_self = cheb(nx, ny, tx, ty)
            score = -d_self
            if score > best_score:
                best_score = score
                best = [dx, dy]
        return best if best is not None else [0, 0]

    min_res_dist_now = min(cheb(x, y, r[0], r[1]) for r in resources)
    # If late in the game, prioritize direct pickup; otherwise deny/contest.
    direct_weight = 2.2 if observation["remaining_resource_count"] <= 4 else 1.2
    deny_weight = 3.0 if observation["remaining_resource_count"] <= 8 else 2.5

    for dx, dy in deltas:
        nx, ny = x + dx, y + dy
        if nx < 0 or ny < 0 or nx >= w or ny >= h or (nx, ny) in obs:
            continue

        self_to_nearest = min(cheb(nx, ny, r[0], r[1]) for r in resources)
        # Deny term: prefer states where our distance advantage over opponent is maximized to some resource.
        deny = -10**18
        for r in resources:
            sd = cheb(nx, ny, r[0], r[1])
            od = cheb(ox, oy, r[0], r[1])
            adv = od - sd  # positive means we are closer
            if adv > deny:
                deny = adv

        # Small bias to not stall when far from resources
        stall_pen = 1 if (dx == 0 and dy == 0 and min_res_dist_now > 1) else 0

        # Also keep some distance from opponent if we're not gaining a deny advantage
        opp_dist = cheb(nx, ny, ox, oy)
        opp_bias = -0.15 * opp_dist

        score = (-direct_weight * self_to_nearest) + (deny_weight * deny) + opp_bias - stall_pen

        if score > best_score:
            best_score = score
            best = [dx, dy]

    return best if best is not None else [0, 0]