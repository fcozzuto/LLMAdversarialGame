def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    resources = [tuple(r) for r in (observation.get("resources", []) or [])]

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

    deltas = [(-1, -1), (0, -1), (1, -1),
              (-1,  0), (0,  0), (1,  0),
              (-1,  1), (0,  1), (1, 1)]

    target = None
    if resources:
        bestd = 10**9
        for rx, ry in resources:
            d = cheb(sx, sy, rx, ry)
            if d < bestd:
                bestd = d
                target = (rx, ry)

    cur_opp_d = cheb(sx, sy, ox, oy)
    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        score = 0
        if target is not None:
            rx, ry = target
            res_d = cheb(nx, ny, rx, ry)
            score += (bestd - res_d) * 30

            # Avoid stepping into opponent's immediate neighborhood unless it helps reach resources.
            opp_d = cheb(nx, ny, ox, oy)
            if opp_d <= 1:
                score -= 60
            elif opp_d <= 2:
                score -= 20
            score += (cur_opp_d - opp_d) * 4

            # Slight bonus for taking a resource cell (exact match).
            if (nx, ny) in obstacles:
                pass
            elif (nx, ny) in set(resources):
                score += 100
        else:
            # If no visible resources, move toward opponent (deterministic).
            opp_d = cheb(nx, ny, ox, oy)
            score += (cur_opp_d - opp_d) * 10

        # Deterministic tie-breaking by move order through strict >
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]