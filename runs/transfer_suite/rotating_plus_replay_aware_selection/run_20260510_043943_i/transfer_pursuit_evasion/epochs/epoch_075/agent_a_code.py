def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    resources = observation.get("resources") or []
    res_list = []
    for r in resources:
        if isinstance(r, dict):
            x = r.get("x", None)
            y = r.get("y", None)
        elif isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
        else:
            continue
        if x is None or y is None:
            continue
        rx, ry = int(x), int(y)
        if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
            res_list.append((rx, ry))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def blocked(nx, ny):
        return not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles

    best = None
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            continue
        dist_to_opp = cheb(nx, ny, ox, oy)
        score = -dist_to_opp * 100
        if res_list:
            dres = min(cheb(nx, ny, rx, ry) for rx, ry in res_list)
            score += max(0, 50 - dres) * 10
        if best is None or score > best_score:
            best_score = score
            best = [dx, dy]
        elif score == best_score and best is not None:
            if (dx, dy) < (best[0], best[1]):
                best = [dx, dy]

    if best is None:
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not blocked(nx, ny):
                return [dx, dy]
        return [0, 0]
    return best