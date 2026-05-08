def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    ox, oy = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    # Choose a target resource we can reach no later than the opponent; otherwise the best "squeeze".
    best = None
    best_key = None
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        # Prefer: reach <= opponent, larger (od-sd), then closer, then tie-break by coordinate.
        reachable_flag = 1 if sd <= od else 0
        key = (reachable_flag, od - sd, -sd, -(abs(rx) * 31 + abs(ry) * 17), -rx, -ry)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best

    # Deterministically pick the move that best reduces our distance to target while not stepping into obstacles.
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    bestm = [0, 0]
    bestmk = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d_self = cheb(nx, ny, tx, ty)
        d_opp = cheb(ox, oy, tx, ty)  # target "pressure" doesn't change in a single step, but used for consistency
        # Penalize moves that allow opponent to be strictly closer by the same turn-step estimate.
        closer_for_opp = 1 if d_self > d_opp else 0
        key = (-closer_for_opp, -d_self, (dx * 3 + dy), -abs(nx - tx) - abs(ny - ty), dx, dy)
        if bestmk is None or key > bestmk:
            bestmk = key
            bestm = [dx, dy]

    return bestm