def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        resources = [(w // 2, h // 2)]

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def cd(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    # Choose the resource that maximizes current advantage (opponent farther than us).
    best_target = resources[0]
    best_adv = cd(ox, oy, best_target[0], best_target[1]) - cd(sx, sy, best_target[0], best_target[1])
    for rx, ry in resources[1:]:
        adv = cd(ox, oy, rx, ry) - cd(sx, sy, rx, ry)
        if adv > best_adv:
            best_adv = adv
            best_target = (rx, ry)
        elif adv == best_adv:
            if cd(sx, sy, rx, ry) < cd(sx, sy, best_target[0], best_target[1]):
                best_target = (rx, ry)

    tx, ty = best_target
    my_here = (sx, sy)
    opp_here = (ox, oy)

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            nx, ny = sx, sy
        my_dist = cd(nx, ny, tx, ty)
        op_dist = cd(ox, oy, tx, ty)
        # Primary: increase our advantage toward chosen target.
        val = (op_dist - my_dist) * 1000
        # Bonus for immediate pickup and for shrinking distance.
        if (nx, ny) in resources:
            if (nx, ny) != my_here:
                val += 50000
            else:
                val += 20000
        # Mild "blocking": slightly discourage moving closer to opponent on their current target direction.
        val -= cd(nx, ny, ox, oy)
        # Deterministic tie-breaker: prefer moves with smaller distance to target, then lexicographic.
        dist_tie = my_dist
        opp_tie = cd(nx, ny, ox, oy)
        key = (val, -dist_tie, -opp_tie, dx, dy)
        if key > (best_val, ) * 4 + (0, 0):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]