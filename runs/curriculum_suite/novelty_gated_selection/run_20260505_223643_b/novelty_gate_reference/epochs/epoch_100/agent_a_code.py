def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
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
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        return [0, 0]

    def mindist(x, y):
        best = 10**9
        for rx, ry in resources:
            d = abs(x - rx) + abs(y - ry)
            if d < best:
                best = d
        return best

    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    best_val = None
    best_move = [0, 0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        self_d = mindist(nx, ny)
        opp_d = mindist(ox, oy)
        # If opponent could be closer to some resource, reduce their advantage:
        # Estimate their best response by also measuring after our move (opponent position unchanged).
        # Main term: maximize (opp_d - self_d).
        on_resource = 1 if (nx, ny) in obstacles else 0
        bonus = 0
        if (nx, ny) in resources:
            bonus += 1000
        # Tie-breakers encourage advancing and not wandering toward the opponent.
        val = (opp_d - self_d, -self_d, md(nx, ny, ox, oy), bonus, -abs(nx - sx) - abs(ny - sy))
        if best_val is None or val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move