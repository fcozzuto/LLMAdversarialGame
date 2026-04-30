def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = observation["obstacles"]
    obs = set((x, y) for x, y in obstacles)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    if not resources:
        tx, ty = ox, oy
    else:
        tx, ty = None, None
        best = -10**18
        for rx, ry in resources:
            myd = (rx - sx) * (rx - sx) + (ry - sy) * (ry - sy)
            opd = (rx - ox) * (rx - ox) + (ry - oy) * (ry - oy)
            # Prefer resources we can reach first; penalize those where opponent is much closer.
            contest = opd - myd
            penalty = 0
            if contest < -2:  # opponent clearly closer
                penalty = (-contest) * 3
            value = (300000 - myd) - penalty + (0.6 * contest)
            if value > best:
                best = value
                tx, ty = rx, ry

    best_move = [0, 0]
    best_val = -10**18
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        # Move selection: go towards target; keep distance from opponent; avoid getting stuck near obstacles.
        ndt = (tx - nx) * (tx - nx) + (ty - ny) * (ty - ny)
        ndo = (ox - nx) * (ox - nx) + (oy - ny) * (oy - ny)
        # Small obstacle proximity penalty
        near_obs = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                px, py = nx + ax, ny + ay
                if 0 <= px < w and 0 <= py < h and (px, py) in obs:
                    near_obs += 1
        val = (-ndt) + 0.25 * ndo - 0.12 * near_obs
        if val > best_val:
            best_val = val
            best_move = [dx, dy]
    return best_move