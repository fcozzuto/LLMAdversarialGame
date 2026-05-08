def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            ax, ay = int(p[0]), int(p[1])
            if 0 <= ax < w and 0 <= ay < h:
                obstacles.add((ax, ay))

    resources = observation.get("resources") or []
    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            rx, ry = int(p[0]), int(p[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                res.append((rx, ry))
        elif isinstance(p, dict):
            rx, ry = int(p.get("x")), int(p.get("y"))
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                res.append((rx, ry))

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    if res:
        best = None
        bestd = None
        for (rx, ry) in res:
            d = abs(rx - sx) + abs(ry - sy)
            if bestd is None or d < bestd:
                bestd = d
                best = (rx, ry)
        tx, ty = best
    else:
        tx, ty = ox, oy

    best_move = (0, 0)
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d_target = abs(tx - nx) + abs(ty - ny)
        d_opp = abs(ox - nx) + abs(oy - ny)
        score = (-d_target, d_opp)  # prioritize approaching target; tie-break by being closer to opponent
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]