def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set((int(x), int(y)) for x, y in obstacles)
    res = [(int(x), int(y)) for x, y in resources if 0 <= int(x) < w and 0 <= int(y) < h]
    if (sx, sy) in obs:
        return [0, 0]
    if not res:
        return [0, 0]
    if (sx, sy) in res:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            nx, ny = sx, sy
            dx, dy = 0, 0
        if (nx, ny) in obs:
            nx, ny = sx, sy
            dx, dy = 0, 0

        # Penalize moves that get us adjacent to obstacles (encourages safer routes)
        adj_pen = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                xx, yy = nx + ax, ny + ay
                if 0 <= xx < w and 0 <= yy < h and (xx, yy) in obs:
                    adj_pen += 1

        # Choose best resource to "win" after this move
        local_best = (-10**18, -10**18)
        for rx, ry in res:
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            advantage = od - sd
            cand = (advantage, -sd)
            if cand > local_best:
                local_best = cand

        val = (local_best[0], local_best[1] - adj_pen * 0.01, -abs(dx) - abs(dy))
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]