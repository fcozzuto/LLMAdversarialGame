def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = observation.get("obstacles") or []
    obs = set((x, y) for x, y in obstacles)

    role = str(observation.get("self_role") or "").lower()
    is_pursuer = ("purs" in role) or ("hunter" in role) or ("chaser" in role)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    def obs_prox(nx, ny):
        if not obs:
            return 10**6
        best = 10**6
        for x, y in obstacles:
            d = abs(nx - x) + abs(ny - y)
            if d < best:
                best = d
        return best

    def cheb(a, b, c, d):
        dx = abs(a - c)
        dy = abs(b - d)
        return dx if dx > dy else dy

    best = None
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        man = abs(nx - ox) + abs(ny - oy)
        prox = obs_prox(nx, ny)

        if is_pursuer:
            # minimize distance; prefer staying away from obstacles
            score = (man, -prox, -abs(dx) - abs(dy), dx, dy)
        else:
            # maximize distance; avoid squares the pursuer can reach next (within 1 step)
            if cheb(nx, ny, ox, oy) <= 1:
                score = (-10**9, 0, 0, dx, dy)
            else:
                score = (-man, -prox, abs(dx) + abs(dy), dx, dy)

        if best_score is None or score < best_score:
            best_score = score
            best = (dx, dy)

    return [best[0], best[1]] if best is not None else [0, 0]