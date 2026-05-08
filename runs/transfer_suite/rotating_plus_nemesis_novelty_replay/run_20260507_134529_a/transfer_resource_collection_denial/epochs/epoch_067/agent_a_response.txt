def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        try:
            obs.add((p[0], p[1]))
        except:
            pass

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def free(x, y):
        return inb(x, y) and (x, y) not in obs

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def dist_cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        best = (-10**9, 0, 0)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny):
                nx, ny = sx, sy
            v = dist_cheb(nx, ny, ox, oy)
            if v > best[0] or (v == best[0] and (nx, ny) < (best[1], best[2])):
                best = (v, nx, ny)
        return [best[1] - sx, best[2] - sy]

    best_score = -10**18
    best = (0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            nx, ny = sx, sy

        cur_best_res = None
        cur_best = (-10**18, 10**18)
        for rx, ry in resources:
            self_d = dist_cheb(nx, ny, rx, ry)
            opp_d = dist_cheb(ox, oy, rx, ry)
            # Prefer targets where we are closer than opponent; also prefer shorter self distance.
            gain = opp_d - self_d
            if gain > cur_best[0] or (gain == cur_best[0] and self_d < cur_best[1]):
                cur_best = (gain, self_d)
                cur_best_res = (rx, ry)

        gain, self_d = cur_best
        # Secondary preference: avoid stepping into the opponent's immediate vicinity when not winning.
        opp_close = dist_cheb(nx, ny, ox, oy)
        score = gain * 100 - self_d - (5 if opp_close <= 1 and gain <= 0 else 0)

        if score > best_score or (score == best_score and (dx, dy) < best):
            best_score = score
            best = (dx, dy)

    return [best[0], best[1]]