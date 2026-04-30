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

    def dist(a, b):
        ax, ay = a; bx, by = b
        return abs(ax - bx) + abs(ay - by)

    best_move = (0, 0)
    best_score = -10**9

    opp_dist_now = cheb((sx, sy), (ox, oy))

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        # distance to nearest resource after move
        if resources:
            ndist = min(cheb((nx, ny), r) for r in resources)
        else:
            ndist = 10**9

        # distance to opponent after move
        opp_after = cheb((nx, ny), (ox, oy))

        # scoring: prioritize approaching resources, keep distance from opponent
        score = (-ndist * 10) + (opp_after * 2)

        # discourage moving into immediate close proximity if currently far
        if opp_after <= 1 and opp_dist_now > 1:
            score -= 50

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]