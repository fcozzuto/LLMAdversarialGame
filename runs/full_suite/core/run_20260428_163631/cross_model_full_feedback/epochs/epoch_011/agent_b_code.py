def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    resources = [tuple(r) for r in observation.get("resources", [])]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(a, b):
        ax, ay = a; bx, by = b
        dx = abs(ax - bx); dy = abs(ay - by)
        return dx if dx > dy else dy

    deltas = [(-1, -1), (0, -1), (1, -1),
              (-1,  0), (0, 0), (1,  0),
              (-1,  1), (0,  1), (1,  1)]

    cur_res_d = min((cheb((sx, sy), r) for r in resources), default=10**9)
    cur_opp_d = cheb((sx, sy), (ox, oy))

    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        if resources:
            res_d = min((cheb((nx, ny), r) for r in resources), default=10**9)
        else:
            res_d = 10**9

        opp_d = cheb((nx, ny), (ox, oy))

        score = 0
        score += (cur_res_d - res_d) * 20
        score += (cur_opp_d - opp_d) * 3

        if (nx, ny) == (ox, oy):
            score -= 5

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]