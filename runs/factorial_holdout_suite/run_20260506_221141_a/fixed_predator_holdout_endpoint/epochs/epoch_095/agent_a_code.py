def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    resources = observation.get("resources") or []
    if not resources:
        return [0, 0]

    obstacles = set()
    for p in observation.get("obstacles") or []:
        x, y = int(p[0]), int(p[1])
        if 0 <= x < w and 0 <= y < h:
            obstacles.add((x, y))

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    res_list = []
    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        if (rx, ry) not in obstacles:
            res_list.append((rx, ry))
    if not res_list:
        return [0, 0]

    # If we are already on a resource, stay to secure it.
    for rx, ry in res_list:
        if rx == sx and ry == sy:
            return [0, 0]

    # Choose move by evaluating best target resource from the candidate position.
    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]

    best_dxdy = None
    best_score = None

    for dx, dy, nx, ny in moves:
        # For each move, pick the resource that maximizes our advantage.
        move_best = None
        for rx, ry in res_list:
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            # Primary: race advantage (we want sd < od). Secondary: closeness. Tertiary: prefer farther from opponent to reduce contention.
            win_adv = od - sd
            # Strongly discourage moves that leave opponent already strictly closer.
            # If win_adv <= 0, still allow but with heavy penalty.
            contention_pen = 0 if win_adv > 0 else 1000 + sd
            cand = (win_adv, -sd, -(max(0, 14 - od)), -contention_pen)
            # Convert to a scalar-ish ordering while staying deterministic.
            if move_best is None or cand > move_best:
                move_best = cand

        # Additional anti-denial: keep distance from opponent slightly (resource_denier often contests).
        opp_dist = man(nx, ny, ox, oy)
        score = (move_best[0], move_best[1], move_best[2], opp_dist)

        if best_score is None or score > best_score:
            best_score = score
            best_dxdy = [dx, dy]

    return best_dxdy if best_dxdy is not None else [0, 0]