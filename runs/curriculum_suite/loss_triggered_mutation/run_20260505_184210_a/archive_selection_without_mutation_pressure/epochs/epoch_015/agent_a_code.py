def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obstacles_list)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def obstacle_pen(nx, ny):
        if not obstacles_list:
            return 0
        best = 99
        for ax, ay in obstacles_list:
            d = abs(nx - ax) + abs(ny - ay)
            if d < best:
                best = d
        return 4 if best <= 1 else (2 if best == 2 else 0)

    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = None
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            d = cheb(nx, ny, cx, cy)
            key = (d + obstacle_pen(nx, ny), dx, dy)
            if best is None or key < best:
                best = key
        return [best[1], best[2]]

    # Pick a move that maximizes how much closer we can be than the opponent to some resource.
    best_move = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        best_adv = None
        best_self_d = None
        for rx, ry in resources:
            self_d = cheb(nx, ny, rx, ry)
            opp_d = cheb(ox, oy, rx, ry)
            adv = opp_d - self_d
            if best_adv is None or adv > best_adv or (adv == best_adv and self_d < best_self_d):
                best_adv = adv
                best_self_d = self_d
        # Prefer higher advantage; if tied, prefer smaller self distance; if still tied, safer/consistent.
        key = (-best_adv, best_self_d + obstacle_pen(nx, ny), abs(nx - ox) + abs(ny - oy), dx, dy)
        if best_move is None or key < best_move:
            best_move = key

    return [best_move[3], best_move[4]]