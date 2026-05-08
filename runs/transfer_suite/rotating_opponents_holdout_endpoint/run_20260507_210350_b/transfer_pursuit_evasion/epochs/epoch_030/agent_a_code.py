def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obs_list = observation.get("obstacles", []) or []
    obstacles = set(tuple(p) for p in obs_list)
    res_list = observation.get("resources", []) or []
    resources = [tuple(p) for p in res_list]
    role = str(observation.get("self_role", "")).lower()

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def in_bounds(x, y): return 0 <= x < w and 0 <= y < h
    def valid(x, y): return in_bounds(x, y) and (x, y) not in obstacles
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2; dx = -dx if dx < 0 else dx
        dy = y1 - y2; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy

    want_escape = any(k in role for k in ("evader", "evade", "runner", "flee", "evasion"))
    best_move = (0, 0)
    best_val = -10**18

    for mdx, mdy in moves:
        nx, ny = sx + mdx, sy + mdy
        if not valid(nx, ny):
            continue
        d_opp = cheb(nx, ny, ox, oy)
        if resources:
            d_res = min(cheb(nx, ny, rx, ry) for rx, ry in resources)
        else:
            d_res = 10**6
        val = 0
        if want_escape:
            val += 20 * d_opp
            val -= d_res
        else:
            val += 20 * (-d_res)
            val += 2 * d_opp
        if val > best_val:
            best_val = val
            best_move = (mdx, mdy)

    return [int(best_move[0]), int(best_move[1])]