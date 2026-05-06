def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", [])
    obs_list = observation.get("obstacles", [])
    obstacles = set((p[0], p[1]) for p in obs_list)
    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Find best contested resource: maximize (opp_dist - our_dist), tie by smaller our_dist then lex
    best_r = None
    best_key = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        od = cheb(ox, oy, rx, ry)
        sd = cheb(sx, sy, rx, ry)
        key = (-(od - sd), sd, rx, ry)  # minimizing negative advantage => maximizing advantage
        if best_key is None or key < best_key:
            best_key = key
            best_r = (rx, ry)

    rx, ry = best_r
    opp_target_dist = cheb(ox, oy, rx, ry)

    # If opponent is already extremely close to that target, switch to our closest resource to race
    if opp_target_dist <= 1:
        chosen = min((resources), key=lambda p: (cheb(sx, sy, p[0], p[1]), p[0], p[1]))
        rx, ry = chosen[0], chosen[1]

    # Move choice: maximize immediate progress toward (rx,ry) while increasing our advantage over opponent
    # Also add mild penalty for stepping into/near obstacles to avoid getting stuck.
    def obs_penalty(x, y):
        p = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                nx, ny = x + ax, y + ay
                if (nx, ny) in obstacles:
                    p += 1
        return p

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        our_d = cheb(nx, ny, rx, ry)
        cur_our_d = cheb(sx, sy, rx, ry)
        opp_d_after = cheb(ox, oy, rx, ry)
        # advantage: how much closer we are than opponent to the target
        advantage = (opp_d_after - our_d)
        progress = cur_our_d - our_d  # positive if closer
        val = advantage * 10 + progress * 2 - obs_penalty(nx, ny) * 0.5
        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]