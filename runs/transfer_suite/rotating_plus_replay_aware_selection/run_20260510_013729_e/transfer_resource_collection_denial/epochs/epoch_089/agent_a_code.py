def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obst = {(x, y) for x, y in (obstacles or [])}
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def legal(x, y):
        return inb(x, y) and (x, y) not in obst

    def md(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    if not resources:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if legal(nx, ny):
                return [dx, dy]
        return [0, 0]

    best_move = (10**18, 0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        res_best = None
        res_dist = 10**18
        for rx, ry in resources:
            d = md(nx, ny, rx, ry)
            if d < res_dist or (d == res_dist and (rx, ry) < res_best):
                res_dist = d
                res_best = (rx, ry)
        rx, ry = res_best
        d_self = md(nx, ny, rx, ry)
        d_opp = md(ox, oy, rx, ry)
        score = d_self - (d_opp // 2)
        if score < best_move[0] or (score == best_move[0] and (dx, dy) < (best_move[1], best_move[2])):
            best_move = (score, dx, dy)

    return [best_move[1], best_move[2]]