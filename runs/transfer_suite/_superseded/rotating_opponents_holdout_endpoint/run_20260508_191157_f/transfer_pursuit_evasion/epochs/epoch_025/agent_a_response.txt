def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = observation.get("obstacles") or []
    obs = set((x, y) for x, y in obstacles)

    role = str(observation.get("self_role") or "").lower()
    is_evader = ("evader" in role) or ("runner" in role) or ("flee" in role) or ("escape" in role)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    def min_obs_dist(nx, ny):
        if not obstacles:
            return 10**6
        m = 10**6
        for x, y in obstacles:
            d = abs(nx - x) + abs(ny - y)
            if d < m:
                m = d
        return m

    def cheb(nx, ny):
        dx = abs(nx - ox)
        dy = abs(ny - oy)
        return dx if dx > dy else dy

    best = (0, 0, None)  # score, obs_dist, move
    # Deterministic tie-break: earlier dirs win on equal score/obs_dist
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d = cheb(nx, ny)
        od = min_obs_dist(nx, ny)
        if is_evader:
            score = d * 1000 + od
        else:
            score = (-d) * 1000 + od
        if best[2] is None or score > best[0] or (score == best[0] and od > best[1]):
            best = (score, od, (dx, dy))

    if best[2] is None:
        return [0, 0]
    return [best[2][0], best[2][1]]