def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def clamp(x, y):
        if x < 0: x = 0
        elif x >= w: x = w - 1
        if y < 0: y = 0
        elif y >= h: y = h - 1
        return x, y

    def dist_cheb(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        ax = dx if dx >= 0 else -dx
        ay = dy if dy >= 0 else -dy
        return ax if ax >= ay else ay

    if not resources:
        return [0, 0]

    best = None  # (advantage, d_self, res_x, res_y, dx, dy)
    for dx, dy in moves:
        nx, ny = clamp(sx + dx, sy + dy)
        if (nx, ny) in obstacles:
            continue
        for rx, ry in resources:
            d_self = dist_cheb(nx, ny, rx, ry)
            d_opp = dist_cheb(ox, oy, rx, ry)
            advantage = d_self - d_opp
            cand = (advantage, d_self, rx, ry, dx, dy)
            if best is None or cand < best:
                best = cand

    if best is None:
        return [0, 0]
    return [int(best[4]), int(best[5])]