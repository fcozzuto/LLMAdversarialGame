def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sx, sy = observation.get("self_position", [0, 0])[:2]
    ox, oy = observation.get("opponent_position", [0, 0])[:2]
    try:
        sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    except:
        sx = sy = ox = oy = 0
    sx = 0 if sx < 0 else (w - 1 if sx >= w else sx)
    sy = 0 if sy < 0 else (h - 1 if sy >= h else sy)
    ox = 0 if ox < 0 else (w - 1 if ox >= w else ox)
    oy = 0 if oy < 0 else (h - 1 if oy >= h else oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
        except:
            pass

    resources = []
    for r in observation.get("resources") or []:
        try:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
        except:
            pass

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_score = None

    if resources:
        target = None
        bestd = None
        for rx, ry in resources:
            d = cheb(sx, sy, rx, ry)
            if bestd is None or d < bestd or (d == bestd and (rx < target[0] if target else True)):
                bestd = d
                target = (rx, ry)
        tx, ty = target
    else:
        tx, ty = w // 2, h // 2

    opp_bias = 0 if resources else 1
    for dx, dy in dirs + [(0, 0)]:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        score = cheb(nx, ny, tx, ty)
        if resources:
            score -= 0.15 * cheb(nx, ny, ox, oy)  # slightly discourage letting opponent get closer
        else:
            score += opp_bias * cheb(nx, ny, ox, oy) * 0.02
        if best_score is None or score < best_score:
            best_score = score
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]