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
        dx = abs(ax - bx)
        dy = abs(ay - by)
        return dx if dx > dy else dy

    deltas = [(-1, -1), (0, -1), (1, -1),
              (-1,  0), (0,  0), (1,  0),
              (-1,  1), (0,  1), (1,  1)]

    target = None
    if resources:
        bestd = 10**9
        for rx, ry in resources:
            d = cheb(sx, sy, rx, ry)
            if d < bestd:
                bestd = d
                target = (rx, ry)

    cur_res_d = 10**9
    if resources:
        cur_res_d = min(cheb(sx, sy, rx, ry) for rx, ry in resources)
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
            score += (cur_res_d - res_d) * 30

        opp_d = cheb(nx, ny, ox, oy)
        # Prefer moving closer to opponent if it reduces their possible access? Keep simple: incentivize distancing
        score += -(opp_d - cur_opp_d) * 2  # discourage moving toward opponent

        # Slight bias to move toward center if possible to potentially access more resources later
        center_x, center_y = w // 2, h // 2
        to_center = cheb(nx, ny, center_x, center_y)
        score += (10 - to_center)

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    # If no valid move found (shouldn't happen), stay
    return [best_move[0], best_move[1]]