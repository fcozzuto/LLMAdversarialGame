def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    resources = [tuple(r) for r in observation.get("resources", [])]

    deltas = [(-1, -1), (0, -1), (1, -1),
              (-1, 0), (0, 0), (1, 0),
              (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def best_res_dist(x, y):
        if not resources:
            return 10**9
        best = 10**9
        for rx, ry in resources:
            d = cheb(x, y, rx, ry)
            if d < best:
                best = d
        return best

    cur_res_d = best_res_dist(sx, sy)
    cur_opp_d = cheb(sx, sy, ox, oy)

    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        res_d = best_res_dist(nx, ny)
        opp_d = cheb(nx, ny, ox, oy)

        score = 0
        # Primary: grab/approach resources
        score += (cur_res_d - res_d) * 25
        score += -res_d * 12
        if res_d == 0:
            score += 10000

        # Secondary: avoid getting too close to opponent unless it also improves resources
        score += opp_d * 3
        if opp_d <= 1:
            score -= 120
            score += (cur_res_d - res_d) * 10

        # Tertiary: prefer moves that also increase opponent's distance from our target area
        if resources:
            # target is nearest resource to us (deterministic proxy)
            tx, ty = resources[0]
            td = cheb(sx, sy, tx, ty)
            for rx, ry in resources[1:]:
                d = cheb(sx, sy, rx, ry)
                if d < td:
                    td = d
                    tx, ty = rx, ry
            # reward if we're moving to keep opponent farther from that target
            opp_to_target_before = cheb(ox, oy, tx, ty)
            opp_to_target_after = cheb(ox, oy, tx, ty)  # opponent doesn't move now; keep simple
            score += (opp_to_target_after - opp_to_target_before) * 2  # always 0, but deterministic
            score += -cheb(nx, ny, tx, ty)  # encourage aiming toward that resource

        if score > best_score or (score == best_score and (dx, dy) == (0, 0)):
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]