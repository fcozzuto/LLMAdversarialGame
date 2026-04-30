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

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    if not ok(sx, sy):
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if ok(nx, ny):
                return [int(dx), int(dy)]
        return [0, 0]

    if resources:
        best = None
        for rx, ry in resources:
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Prefer resources we are closer to; penalize those opponent is likely to take.
            val = ds - 0.9 * do
            # Tie-break deterministically toward our quadrant/axis.
            tie = (rx - sx) * (rx - sx) + (ry - sy) * (ry - sy)
            key = (val, tie, rx, ry)
            if best is None or key < best[0]:
                best = (key, (rx, ry))
        rx, ry = best[1]
        # Greedy one-step toward chosen resource while staying valid and lightly avoiding opponent.
        best_move = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            d_to = cheb(nx, ny, rx, ry)
            d_from_opp = cheb(nx, ny, ox, oy)
            # Higher d_from_opp is better; also reduce distance to resource.
            score = (d_to, -d_from_opp, (dx, dy))
            if best_move is None or score < best_move[0]:
                best_move = (score, (dx, dy))
        if best_move is not None:
            return [int(best_move[1][0]), int(best_move[1][1])]

    # No resources or no valid moves: retreat from opponent, drift toward center.
    best_move = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        dist_opp = cheb(nx, ny, ox, oy)
        dist_center = (nx - cx) * (nx - cx) + (ny - cy) * (ny - cy)
        score = (-dist_opp, dist_center, (dx, dy))
        if best_move is None or score < best_move[0]:
            best_move = (score, (dx, dy))
    if best_move is not None:
        return [int(best_move[1][0]), int(best_move[1][1])]
    return [0, 0]