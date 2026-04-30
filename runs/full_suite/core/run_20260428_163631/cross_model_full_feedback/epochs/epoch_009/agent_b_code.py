def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    resources = [tuple(r) for r in observation.get("resources", [])]

    deltas = [(-1, -1), (0, -1), (1, -1),
              (-1,  0), (0, 0), (1,  0),
              (-1,  1), (0,  1), (1,  1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(a, b):
        ax, ay = a; bx, by = b
        dx = abs(ax - bx); dy = abs(ay - by)
        return dx if dx > dy else dy

    def best_res_dist(x, y):
        if not resources:
            return 10**9
        best = 10**9
        for rx, ry in resources:
            d = cheb((x, y), (rx, ry))
            if d < best:
                best = d
        return best

    cur_res_d = best_res_dist(sx, sy)
    cur_opp_d = cheb((sx, sy), (ox, oy))

    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        res_d = best_res_dist(nx, ny)
        opp_d = cheb((nx, ny), (ox, oy))

        score = 0
        score += (cur_res_d - res_d) * 20
        score += (cur_opp_d - opp_d) * 3

        if (nx, ny) == (ox, oy):
            score -= 5

        if dx == 0 and dy == 0:
            score -= 1

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]