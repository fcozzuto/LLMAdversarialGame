def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    resources = [tuple(r) for r in observation.get("resources", [])]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist_cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def best_res_dist(nx, ny):
        if not resources:
            return 10**9
        best = 10**9
        for rx, ry in resources:
            d = dist_cheb(nx, ny, rx, ry)
            if d < best:
                best = d
        return best

    best_move = (0, 0)
    best_score = -10**18

    opp_d_now = dist_cheb(sx, sy, ox, oy)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        res_d = best_res_dist(nx, ny)
        opp_d = dist_cheb(nx, ny, ox, oy)

        # Prefer closer resources; prefer not getting too close to opponent.
        score = (-res_d * 10) + (opp_d * 2)
        if opp_d <= 1 and opp_d_now > 1:
            score -= 50
        if (dx, dy) < best_move and score == best_score:
            continue

        if score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]