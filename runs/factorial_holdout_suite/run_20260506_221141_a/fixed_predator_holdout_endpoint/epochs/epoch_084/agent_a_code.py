def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        x, y = int(p[0]), int(p[1])
        if 0 <= x < w and 0 <= y < h:
            obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        x, y = int(r[0]), int(r[1])
        if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
            resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_move = [0, 0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h): 
            continue
        if (nx, ny) in obstacles:
            continue

        # Evaluate this step by best resource we can contest soonest
        local_best = None
        for rx, ry in resources:
            my_d = cheb(nx, ny, rx, ry)
            opp_d = cheb(ox, oy, rx, ry)
            # Primary: maximize lead (opp_d - my_d); Secondary: minimize my_d; Tertiary: prefer resources nearer center
            lead = opp_d - my_d
            center_bias = -abs(rx - (w - 1) / 2.0) - abs(ry - (h - 1) / 2.0)
            key = (lead, -my_d, center_bias)
            if (local_best is None) or (key > local_best[0]):
                local_best = (key, rx, ry, my_d, opp_d)
        if local_best is None:
            continue

        # Additional tie-break: reduce distance to opponent if we are behind (resource denier matchup)
        _, rx, ry, my_d, opp_d = local_best
        behind_penalty = 0
        if opp_d > my_d:
            behind_penalty = cheb(nx, ny, ox, oy) * 0.001
        key2 = (local_best[0][0], local_best[0][1], local_best[0][2] - behind_penalty, -cheb(nx, ny, rx, ry), -rx, -ry)
        if (best is None) or (key2 > best):
            best = key2
            best_move = [dx, dy]

    return best_move