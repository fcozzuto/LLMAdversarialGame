def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(map(tuple, observation.get("obstacles", [])))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def sd(x1, y1, x2, y2):  # squared distance
        dx = x1 - x2; dy = y1 - y2
        return dx * dx + dy * dy

    # Choose a "safer" target: close to self, but far from opponent.
    if resources:
        best = None
        for rx, ry in resources:
            self_d = sd(sx, sy, rx, ry)
            opp_d = sd(ox, oy, rx, ry)
            key = (self_d - 0.55 * opp_d, rx, ry)  # deterministic
            if best is None or key < best[0]:
                best = (key, (rx, ry))
        tx, ty = best[1]
    else:
        tx, ty = ox, oy

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    # Deterministic tie-break via move order only
    best_move = (0, 0); best_score = None

    # Obstacle influence
    obs_list = list(obstacles)
    def nearest_obs_dist2(x, y):
        if not obs_list: return 999999
        dmin = None
        for ax, ay in obs_list:
            d = sd(x, y, ax, ay)
            if dmin is None or d < dmin: dmin = d
        return dmin

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        # Resource capture: huge reward
        on_res = 0
        for rx, ry in resources:
            if rx == nx and ry == ny:
                on_res = 1
                break

        d_tar = sd(nx, ny, tx, ty)
        d_opp = sd(nx, ny, ox, oy)

        # Prefer staying away from obstacles; also avoid getting too close to opponent
        d_obs = nearest_obs_dist2(nx, ny)
        obs_score = 0.15 * min(200.0, d_obs)

        # Encourage moving closer to target; discourage approaching opponent
        score = 0.0
        score += 5000.0 * on_res
        score += -1.1 * d_tar
        score += 0.05 * min(800.0, d_opp)  # farther is better
        score += obs_score

        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]