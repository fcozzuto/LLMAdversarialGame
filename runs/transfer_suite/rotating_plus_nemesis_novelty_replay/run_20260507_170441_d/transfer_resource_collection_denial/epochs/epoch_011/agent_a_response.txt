def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    if not resources:
        return [0, 0]

    obst_set = {tuple(p) for p in obstacles}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def d2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    # Choose target resource where we are closer than opponent, breaking ties deterministically
    best_r = None
    best_gain = -10**18
    for rx, ry in resources:
        myd = d2(sx, sy, rx, ry)
        opd = d2(ox, oy, rx, ry)
        gain = opd - myd
        if gain > best_gain or (gain == best_gain and (rx, ry) < tuple(best_r)):
            best_gain = gain
            best_r = [rx, ry]
    tx, ty = best_r

    cand = [(0, 0), (-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    best_move = [0, 0]
    best_val = 10**30

    # Obstacle avoidance: prefer moves that keep distance from obstacles
    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obst_set:
            continue

        my_dt = d2(nx, ny, tx, ty)
        opp_dt = d2(nx, ny, ox, oy)

        if obstacles:
            min_ob = 10**18
            for px, py in obstacles:
                v = d2(nx, ny, px, py)
                if v < min_ob:
                    min_ob = v
        else:
            min_ob = 10**18

        # Lower is better: go toward target, also keep away from obstacles and slightly away from opponent
        val = my_dt - 0.15 * opp_dt
        if obstacles:
            # Stronger penalty when close to any obstacle
            val += 8.0 / (min_ob + 1)

        # Tie-break deterministically by move preference order
        if val < best_val or (val == best_val and (dx, dy) < tuple(best_move)):
            best_val = val
            best_move = [dx, dy]

    return best_move