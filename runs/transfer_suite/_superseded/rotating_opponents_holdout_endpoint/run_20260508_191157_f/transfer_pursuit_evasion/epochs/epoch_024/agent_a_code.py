def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = observation.get("obstacles") or []
    obs = set((x, y) for x, y in obstacles)

    role = str(observation.get("self_role") or "").lower()
    is_pursuer = ("purs" in role) or ("hunter" in role) or ("chaser" in role) or ("attacker" in role)

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

    best_move = (0, 0)
    best_key = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d = cheb(nx, ny)
        prox = min_obs_dist(nx, ny)

        # Deterministic tie-break ordering is handled by strict lexicographic keys and fixed move iteration.
        if is_pursuer:
            # Chase: minimize distance to opponent; keep away from obstacles; prefer smaller movement (stability)
            key = (d, -prox, abs(dx) + abs(dy), dx, dy)
            if best_key is None or key < best_key:
                best_key = key
                best_move = (dx, dy)
        else:
            # Evade: maximize distance; keep away from obstacles; prefer reducing potential pursuit (increase Chebyshev strongly)
            key = (-d, -prox, -(abs(dx) + abs(dy)), dx, dy)
            if best_key is None or key < best_key:
                best_key = key
                best_move = (dx, dy)

    return [best_move[0], best_move[1]]