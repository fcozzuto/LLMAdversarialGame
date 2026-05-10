def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    is_evader = str(observation.get("self_role", "")).lower() == "evader"

    obstacles = list(obs)
    def dist_to_obs(x, y):
        if not obstacles:
            return 10
        md = 10**9
        for ex, ey in obstacles:
            d = abs(x - ex) + abs(y - ey)
            if d < md:
                md = d
        return md

    def score_move(x, y):
        dxo, dyo = x - ox, y - oy
        d_opp = dxo * dxo + dyo * dyo  # squared euclidean
        d_obs = dist_to_obs(x, y)
        if is_evader:
            # Run away, but prefer having "space" from obstacles to avoid being funneled.
            return d_opp + 0.7 * d_obs - 0.03 * (abs(x - 3.5) + abs(y - 3.5))
        else:
            # Pursuer: greedy chase while keeping clear of obstacles.
            return -d_opp + 0.6 * d_obs

    best = [0, 0]
    best_sc = None
    order = sorted(moves, key=lambda t: (t[0], t[1]))
    for dx, dy in order:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        sc = score_move(nx, ny)
        if best_sc is None or sc > best_sc:
            best_sc = sc
            best = [dx, dy]
    return best