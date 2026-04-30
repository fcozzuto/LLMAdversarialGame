def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    resources = [tuple(r) for r in observation.get("resources", [])]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (0, -1), (1, -1),
              (-1, 0), (0, 0), (1, 0),
              (-1, 1), (0, 1), (1, 1)]

    cur_res_best = 10**9
    cur_opp = cheb(sx, sy, ox, oy)
    if resources:
        for rx, ry in resources:
            d = cheb(sx, sy, rx, ry)
            if d < cur_res_best:
                cur_res_best = d

    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        opp_d = cheb(nx, ny, ox, oy)

        if resources:
            # Choose target that we can contest: maximize (opp_dist - self_dist)
            best_contest = -10**18
            best_self_dist = 10**9
            best_res_d = 10**9
            for rx, ry in resources:
                sd = cheb(nx, ny, rx, ry)
                od = cheb(ox, oy, rx, ry)
                if sd < best_self_dist:
                    best_self_dist = sd
                    best_res_d = sd
                cont = od - sd
                if cont > best_contest:
                    best_contest = cont
            # If we are already adjacent to any resource, strongly prefer that.
            nearest_d = best_self_dist
        else:
            best_contest = 0
            nearest_d = 10**9
            best_self_dist = 10**9
            best_res_d = 10**9

        # Score components:
        # - Contest advantage over opponent at resources
        # - Direct progress toward nearest resource
        # - Keep some distance from opponent (but not at the cost of contesting resources)
        progress = 0
        if resources:
            cur_best = cur_res_best
            progress = cur_best - best_self_dist

        score = 0
        score += best_contest * 30
        score += progress * 12
        score += (10**6 // (nearest_d + 1))  # greedy attraction to nearby resources
        score += min(opp_d, 10) * 1.5       # mild repulsion

        # If opponent is extremely close, prefer moves that increase distance unless it hurts contest.
        if opp_d <= 1:
            score += (opp_d * -20)

        # Slight preference for staying still if no meaningful gradients
        if dx == 0 and dy == 0:
            score += 0.5

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]