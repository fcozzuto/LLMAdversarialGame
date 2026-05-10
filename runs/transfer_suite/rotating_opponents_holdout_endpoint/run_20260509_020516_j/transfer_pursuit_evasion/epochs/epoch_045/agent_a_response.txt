def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for it in observation.get("obstacles") or []:
        if isinstance(it, dict):
            x, y = it.get("x"), it.get("y")
        else:
            x, y = it[0], it[1]
        if x is None or y is None:
            continue
        x, y = int(x), int(y)
        if 0 <= x < w and 0 <= y < h:
            obstacles.add((x, y))

    role = (observation.get("self_role") or "").lower()
    is_evader = ("evader" in role) or ("runner" in role) or ("escape" in role)
    is_pursuer = ("pursuer" in role) or ("chaser" in role) or ("catcher" in role)
    if not (is_evader or is_pursuer):
        is_pursuer = True

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Corner bias for evader (flee toward the corner farthest from pursuer)
    target_corner = None
    if is_evader:
        bestc = None
        bestd = -1
        for cx, cy in corners:
            d = md(cx, cy, ox, oy)
            if d > bestd:
                bestd = d
                bestc = (cx, cy)
        target_corner = bestc

    best_move = [0, 0]
    if is_pursuer:
        best_score = -10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            d = md(nx, ny, ox, oy)
            # Prefer minimizing distance; tie-break by aligning toward opponent
            score = -d * 100 - (abs((nx - ox)) + abs((ny - oy)))
            if score > best_score:
                best_score = score
                best_move = [dx, dy]
            elif score == best_score:
                if (dx, dy) < (best_move[0], best_move[1]):
                    best_move = [dx, dy]
    else:
        best_score = -10**9
        tcx, tcy = target_corner
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            d = md(nx, ny, ox, oy)
            corner_d = md(nx, ny, tcx, tcy)
            # Prefer maximizing distance; also prefer moving toward the selected corner
            score = d * 100 - corner_d
            if score > best_score:
                best_score = score
                best_move = [dx, dy]
            elif score == best_score:
                if (dx, dy) > (best_move[0], best_move[1]):
                    best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]