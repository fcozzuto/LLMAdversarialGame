def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw = observation.get("grid_width", 8)
    gh = observation.get("grid_height", 8)
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set((x, y) for x, y in obstacles)

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    def blocked(x, y):
        return (not inb(x, y)) or ((x, y) in obs)

    def king_dist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def obs_adj_pen(x, y):
        p = 0
        for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)):
            if (x + dx, y + dy) in obs:
                p += 1
        return p

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not moves:
        return [0, 0]

    next_targets = resources
    best_overall = -10**18
    best_move = [0, 0]

    for mx, my in moves:
        nx, ny = sx + mx, sy + my
        if blocked(nx, ny):
            continue

        hit_resource = 1 if (nx, ny) in set((r[0], r[1]) for r in resources) else 0
        adj_pen = obs_adj_pen(nx, ny)
        opp_now = king_dist(nx, ny, ox, oy)

        if not resources:
            # No resources: head toward opponent to force contention / blocking
            score = -opp_now - 0.5 * adj_pen
        else:
            # Choose the resource where we are closest relative to the opponent
            best_adv = -10**18
            best_d_self = 10**18
            for rx, ry in resources:
                ds = king_dist(nx, ny, rx, ry)
                do = king_dist(ox, oy, rx, ry)
                adv = do - ds  # positive means we are closer than opponent
                if adv > best_adv or (adv == best_adv and ds < best_d_self):
                    best_adv = adv
                    best_d_self = ds

            # Combine: win priority for positive advantage, otherwise minimize our distance
            if best_adv >= 0:
                score = 200 + 20 * best_adv - 2 * best_d_self - 1.5 * adj_pen
            else:
                score = 50 + 10 * best_adv - 1.5 * best_d_self - 1.5 * adj_pen

            score += 5 * hit_resource

        if score > best_overall:
            best_overall = score
            best_move = [mx, my]

    return best_move