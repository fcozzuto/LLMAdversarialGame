def choose_move(observation):
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation["obstacles"]
    obs_set = set((p[0], p[1]) for p in obstacles)
    resources = observation["resources"]

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def clamp_move(nx, ny):
        if nx < 0 or ny < 0 or nx >= observation["grid_width"] or ny >= observation["grid_height"]:
            return False
        if (nx, ny) in obs_set:
            return False
        return True

    def dist(a, b):
        ax, ay = a; bx, by = b
        dx = ax - bx; dy = ay - by
        return (dx*dx + dy*dy)

    # If no resources, just move away from opponent while staying legal.
    if not resources:
        best = (None, -10**18)
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if not clamp_move(nx, ny): 
                continue
            score = dist((nx, ny), (ox, oy))
            if score > best[1]:
                best = ((dx, dy), score)
        if best[0] is None:
            return [0, 0]
        return [best[0][0], best[0][1]]

    # Choose a target resource we can reach earlier (or at least challenge) deterministically.
    best_res = resources[0]
    best_res_score = -10**18
    for rx, ry in resources:
        ds = dist((x, y), (rx, ry))
        do = dist((ox, oy), (rx, ry))
        # Favor resources where we're closer (ds smaller); also slightly favor globally closer squares.
        score = (do - ds) - 0.05 * (ds + do)
        if score > best_res_score:
            best_res_score = score
            best_res = (rx, ry)

    rx, ry = best_res

    # Evaluate moves by: closer to target, farther from opponent, and reduce risk of giving up target.
    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if not clamp_move(nx, ny):
            continue
        d_target = dist((nx, ny), (rx, ry))
        d_opp = dist((nx, ny), (ox, oy))
        d_opp_to_target = dist((ox, oy), (rx, ry))
        # If we reach target square next, get big bonus.
        on_target = 1 if (nx == rx and ny == ry) else 0
        # Encourage moves that also make opponent relatively worse at the chosen target.
        relative = d_opp_to_target - d_target
        score = (-d_target) + 0.08 * d_opp + 0.6 * relative + 5.0 * on_target
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]