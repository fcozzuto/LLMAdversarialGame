def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    tx, ty = None, None
    if resources:
        best = None
        for (x, y) in resources:
            d = cheb(sx, sy, x, y)
            if best is None or d < best[0] or (d == best[0] and (x, y) < best[1]):
                best = (d, (x, y))
        tx, ty = best[1]
    else:
        tx, ty = (w - 1) // 2, (h - 1) // 2

    cur_opp_d = cheb(sx, sy, ox, oy)
    best_move = (0, 0)
    best_score = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d = cheb(nx, ny, tx, ty)
        opp_d = cheb(nx, ny, ox, oy)

        score = d * 1000  # primary: get closer to target
        # secondary: prefer moves that don't allow opponent to get too close
        score -= opp_d
        # tertiary: lightly prefer staying away from obstacles by discouraging moves into tight corners
        tight = 0
        for ax, ay in dirs:
            px, py = nx + ax, ny + ay
            if valid(px, py) is False:
                tight += 1
        score += tight

        # deterministic tie-break: smaller dx, then dy
        if best_score is None or score < best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    dx, dy = best_move
    if dx not in (-1, 0, 1) or dy not in (-1, 0, 1):
        return [0, 0]
    return [dx, dy]