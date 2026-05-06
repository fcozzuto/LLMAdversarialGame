def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    # Determine preferred resource by relative reach (after our move).
    def best_relative_value(px, py):
        best = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            da = cheb(px, py, rx, ry)
            do = cheb(ox, oy, rx, ry)
            if best is None or (do - da, -da, -rx, -ry) > (best[0], -best[1], best[2], best[3]):
                best = (do - da, da, rx, ry)
        return best

    # If no usable resources, head to opponent to deny.
    def deny_value(px, py):
        return -cheb(px, py, ox, oy)

    best_move = (0, 0)
    best_score = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            score = -10**9 + (dx == 0 and dy == 0)
        else:
            if resources:
                br = best_relative_value(nx, ny)
                if br is None:
                    score = deny_value(nx, ny)
                else:
                    rel, da, rx, ry = br
                    # Prefer being closer ourselves, and also slightly prefer resources not too close to opponent.
                    opp_near = cheb(ox, oy, rx, ry)
                    score = rel * 10 - da - opp_near * 0.25
            else:
                score = deny_value(nx, ny)

        cand = (score, -abs(dx) - abs(dy), dx, dy)
        if best_score is None or cand > best_score:
            best_score = cand
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]