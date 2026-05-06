def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    obstacles = set(tuple(p) for p in observation["obstacles"])
    resources = [tuple(p) for p in observation["resources"]]

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]
    if not resources:
        # maximize distance from opponent
        best = None
        for dx, dy, nx, ny in moves:
            d = abs(nx - ox) + abs(ny - oy)
            if best is None or d > best[0]:
                best = (d, dx, dy)
        return [best[1], best[2]]

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    best_move = (None, -10**18, 0, 0, 0, 0)
    for dx, dy, nx, ny in moves:
        # one-step look: pick the resource that gives best contested advantage after this move
        best_res_score = -10**18
        best_res_dist = 10**9
        for rx, ry in resources:
            ds = dist((nx, ny), (rx, ry))
            do = dist((ox, oy), (rx, ry))
            # contested advantage: positive means we are closer
            adv = do - ds
            # if opponent is already as close or closer, penalize heavily (try to "cut off" instead)
            penalty = 0
            if do <= ds:
                penalty += 30 + 5 * (ds - do)
            # if we can reach significantly sooner, reward more
            reward = 0
            if ds + 1 <= do:
                reward += 10 + 2 * (do - ds)
            # slight center bias to break ties deterministically
            center = -(abs(rx - (gw - 1) / 2.0) + abs(ry - (gh - 1) / 2.0)) * 0.01
            score = adv + reward - penalty + center
            if score > best_res_score or (score == best_res_score and ds < best_res_dist):
                best_res_score = score
                best_res_dist = ds

        # if overall we are likely losing for all resources, switch strategy: move to increase ds to contested set
        # compute how many resources opponent currently has an edge on
        losing = 0
        for rx, ry in resources:
            if dist((ox, oy), (rx, ry)) <= dist((nx, ny), (rx, ry)):
                losing += 1
        risk_adjust = -2 * losing

        # final score for this move
        final = best_res_score + risk_adjust
        if final > best_move[1]:
            best_move = (dx, final, dx, dy, nx, ny)

    return [best_move[2], best_move[3]]