def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    obs_list = observation.get("obstacles", [])
    obstacles = set()
    for p in obs_list:
        obstacles.add((p[0], p[1]))

    resources = observation.get("resources", [])
    if resources:
        best_t = None
        best_d = 10**9
        for r in resources:
            tx, ty = r[0], r[1]
            d = max(abs(tx - sx), abs(ty - sy))
            if d < best_d:
                best_d = d
                best_t = (tx, ty)
        tx, ty = best_t
    else:
        tx, ty = (w - 1) // 2, (h - 1) // 2

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        return max(abs(x1 - x2), abs(y1 - y2))

    best_score = 10**18
    best_move = [0, 0]

    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            if (nx, ny) in obstacles:
                continue
            if (nx, ny) == (ox, oy):
                continue
            d_self = cheb(nx, ny, tx, ty)
            d_opp = cheb(nx, ny, ox, oy)
            center_bias = abs(nx - (w - 1) / 2) + abs(ny - (h - 1) / 2)
            score = d_self * 1000 - d_opp * 5 + center_bias * 0.001
            if score < best_score:
                best_score = score
                best_move = [dx, dy]
    return best_move