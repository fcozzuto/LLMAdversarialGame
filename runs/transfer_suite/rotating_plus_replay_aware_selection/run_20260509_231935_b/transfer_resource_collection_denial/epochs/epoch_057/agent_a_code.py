def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    res = [(p[0], p[1]) for p in resources if p and len(p) >= 2]
    obs = set((p[0], p[1]) for p in obstacles if p and len(p) >= 2)

    dirs = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    if not res:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    best_move = [0, 0]
    best_score = -10**18
    best_selfd = 10**9

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obs:
            continue

        # Choose a target resource that maximizes our "steal" advantage vs opponent.
        move_best_adv = -10**18
        move_best_sd = 10**9
        for rx, ry in res:
            if (rx, ry) in obs:
                continue
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            adv = od - sd
            if adv > move_best_adv or (adv == move_best_adv and (sd < move_best_sd)):
                move_best_adv = adv
                move_best_sd = sd

        # Prefer larger advantage; if tie, prefer smaller self distance; then lex.
        if (move_best_adv > best_score or
            (move_best_adv == best_score and (move_best_sd < best_selfd)) or
            (move_best_adv == best_score and move_best_sd == best_selfd and (dx > best_move[0] or (dx == best_move[0] and dy > best_move[1])))):
            best_score = move_best_adv
            best_selfd = move_best_sd
            best_move = [dx, dy]

    return best_move