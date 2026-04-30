def choose_move(observation):
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = {tuple(p) for p in observation["obstacles"]}
    resources = [tuple(p) for p in observation["resources"]]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def in_bounds(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def cheb(a, b):
        ax, ay = a
        bx, by = b
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def score_pos(nx, ny):
        if (nx, ny) in obstacles:
            return -10**9
        if resources:
            best_adv = -10**9
            best_my = 10**9
            for r in resources:
                myd = cheb((nx, ny), r)
                opd = cheb((ox, oy), r)
                adv = (opd - myd) * 10 - myd
                if adv > best_adv:
                    best_adv = adv
                    best_my = myd
            sep = cheb((nx, ny), (ox, oy))
            return best_adv + sep * 0.25 - best_my * 0.02
        cx, cy = (w - 1) // 2, (h - 1) // 2
        return -cheb((nx, ny), (cx, cy)) - cheb((nx, ny), (ox, oy)) * 0.05

    best_score = -10**18
    best_move = [0, 0]
    for dx, dy in deltas:
        nx, ny = x + dx, y + dy
        if in_bounds(nx, ny):
            s = score_pos(nx, ny)
            if s > best_score:
                best_score = s
                best_move = [dx, dy]
    return best_move