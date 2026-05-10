def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles", []) or []
    obs = set((int(p[0]), int(p[1])) for p in obstacles)

    resources = observation.get("resources", []) or []
    res = [(int(p[0]), int(p[1])) for p in resources]

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def blocked(x, y):
        return (x, y) in obs

    has_res = len(res) > 0
    if has_res:
        best_res_dist = min(abs(x - sx) + abs(y - sy) for x, y in res)
    else:
        best_res_dist = 0

    def score_pos(x, y):
        if not inb(x, y) or blocked(x, y):
            return -10**9

        d_opp = abs(x - ox) + abs(y - oy)
        if has_res:
            d_res = min(abs(x - rx) + abs(y - ry) for rx, ry in res)
            return 50 * (d_opp) - 100 * d_res + 3 * (d_opp == best_res_dist)
        return 100 * d_opp

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        sc = score_pos(nx, ny)
        if sc > best_score:
            best_score = sc
            best_move = (dx, dy)
    return [best_move[0], best_move[1]]