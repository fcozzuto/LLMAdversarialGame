def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obs_list = observation.get("obstacles") or []
    obstacles = set((p[0], p[1]) for p in obs_list)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < gw and 0 <= y < gh

    def legal(x, y):
        return in_bounds(x, y) and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    if not resources:
        tx = gw - 1 if sx < gw // 2 else 0
        ty = gh - 1 if sy < gh // 2 else 0
        best = [0, 0]
        bestv = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            v = -cheb(nx, ny, tx, ty)
            if v > bestv:
                bestv = v
                best = [dx, dy]
        return best

    opp_better_wins = 2 if len(resources) >= 6 else 3
    best_move, best_val = [0, 0], -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue

        best_cell = -10**18
        for rx, ry in resources:
            d_me = cheb(nx, ny, rx, ry)
            d_opp = cheb(ox, oy, rx, ry)
            # Prefer taking resources where we are closer than opponent; otherwise minimize our distance.
            rel = d_opp - d_me
            if rel >= 0:
                v = rel * 100 - d_me
            else:
                v = rel * 100 / opp_better_wins - d_me
            if v > best_cell:
                best_cell = v
        # Encourage moving toward the globally best target (avoid oscillation by preferring lower distance to the best resource).
        tie_adj = 0
        min_d = 10**9
        for rx, ry in resources:
            d = cheb(nx, ny, rx, ry)
            if d < min_d:
                min_d = d
        tie_adj = -min_d * 2

        total = best_cell + tie_adj
        if total > best_val:
            best_val = total
            best_move = [dx, dy]

    return best_move