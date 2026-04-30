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

    # Target nearest resource if any
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

        # Proximity to opponent: discourage moving into close to opponent
        opp_dist = cheb(nx, ny, ox, oy)
        score -= max(0, 2 - opp_dist)

        # If resource target exists, prioritize approaching it and denying opponent
        if target is not None:
            rx, ry = target
            res_d = cheb(nx, ny, rx, ry)
            score += (cur_res_d - res_d) * 4
            # discourage moving away from resource if already near
            score += max(0, 2 - res_d)

            # try to stay closer to resources than opponent
            od = cheb(nx, ny, ox, oy)
            score += max(0, (od - res_d))

        # Simple safety: avoid stalling near walls when not near resource
        if target is None:
            dist_to_center = cheb(nx, ny, w//2, h//2)
            score += max(0, (3 - dist_to_center))

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    # If no valid move found, stay
    if best_move is None:
        best_move = (0, 0)
    return [best_move[0], best_move[1]]