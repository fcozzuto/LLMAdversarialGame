def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    if w <= 0 or h <= 0:
        return [0, 0]
    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = (0, 0, -10**18)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            v = -cheb(nx, ny, cx, cy) - 0.01*(nx + ny)
            if v > best[2]:
                best = (dx, dy, v)
        return [best[0], best[1]]

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        my_win = 0.0
        opp_win = 0.0
        my_best = 10**9
        for rx, ry in resources:
            md = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            if md < od:
                my_win += 1.0
                if md < my_best: my_best = md
            elif od < md:
                opp_win += 1.0
        # Encourage faster capture, discourage giving up many resources
        val = (my_win - opp_win) * 10.0 - my_best * 0.1
        # Tiny deterministic tiebreaker favor moving toward higher x then y
        val += (nx * 0.001 + ny * 0.0001)
        if val > best_val:
            best_val = val
            best_move = (dx, dy)
    return [best_move[0], best_move[1]]