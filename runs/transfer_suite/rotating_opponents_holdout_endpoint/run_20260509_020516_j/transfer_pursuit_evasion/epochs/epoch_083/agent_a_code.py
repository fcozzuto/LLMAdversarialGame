def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for it in (observation.get("obstacles") or []):
        try:
            if isinstance(it, dict):
                x, y = it.get("x"), it.get("y")
            else:
                x, y = it[0], it[1]
            x, y = int(x), int(y)
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
        except Exception:
            pass

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def obstacle_farness(x, y):
        best = 999
        for (ax, ay) in obstacles:
            dx = x - ax
            if dx < 0: dx = -dx
            dy = y - ay
            if dy < 0: dy = -dy
            d = dx if dx > dy else dy
            if d < best:
                best = d
                if best == 0:
                    return 0
        return best

    is_evader = "evader" in (observation.get("self_role") or "").lower()
    curd = cheb(sx, sy, ox, oy)

    best = (0, 0)
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        nd = cheb(nx, ny, ox, oy)
        if (nx, ny) == (ox, oy) and not is_evader:
            return [dx, dy]

        # Primary objective: approach for pursuer, evade for evader
        if is_evader:
            # want larger distance; also avoid dead-ends near obstacles
            prim = nd
            # preference to increase distance relative to current when possible
            delta = nd - curd
            score = (prim, delta, obstacle_farness(nx, ny), -dx, -dy)
            if best_score is None or score > best_score:
                best_score = score
                best = (dx, dy)
        else:
            # want smaller distance; also prefer moves away from obstacles when tying
            prim = -nd
            delta = curd - nd
            score = (prim, delta, obstacle_farness(nx, ny), -dx, -dy)
            if best_score is None or score > best_score:
                best_score = score
                best = (dx, dy)

    return [int(best[0]), int(best[1])]