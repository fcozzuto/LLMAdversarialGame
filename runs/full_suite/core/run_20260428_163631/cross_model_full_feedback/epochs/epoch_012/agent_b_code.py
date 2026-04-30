def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obstacles = set(tuple(p) for p in observation.get("obstacles", []) or [])
    resources = [tuple(r) for r in observation.get("resources", []) or []]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(a_x, a_y, b_x, b_y):
        dx = abs(a_x - b_x)
        dy = abs(a_y - b_y)
        return dx if dx > dy else dy

    deltas = [(-1, -1), (0, -1), (1, -1),
              (-1,  0), (0, 0), (1,  0),
              (-1,  1), (0,  1), (1,  1)]

    cur_res_d = min((cheb(sx, sy, rx, ry) for rx, ry in resources), default=10**9)
    cur_opp_d = cheb(sx, sy, ox, oy)

    best_move = (0, 0)
    best_score = -10**18

    near_res = None
    if resources:
        near_res = min(resources, key=lambda r: cheb(sx, sy, r[0], r[1]))

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        if resources:
            res_d = min((cheb(nx, ny, rx, ry) for rx, ry in resources), default=10**9)
        else:
            res_d = 10**9

        opp_d = cheb(nx, ny, ox, oy)

        score = 0
        score += (cur_res_d - res_d) * 20
        score += (cur_opp_d - opp_d) * 3

        if (nx, ny) == (ox, oy):
            score -= 5

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]