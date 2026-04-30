def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # pick a target resource favoring those we are closer to than opponent
    scored = []
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        advantage = od - sd  # positive means we are closer
        # mild bonus for resources nearer to our side (deterministic shaping)
        side_bonus = (rx + ry) * 0.001  # small tie-breaker
        score = advantage * 2.0 - sd + side_bonus
        scored.append((score, rx, ry, sd, od))
    scored.sort(key=lambda t: (-t[0], t[3], t[1], t[2]))
    target = (scored[0][1], scored[0][2])
    tx, ty = target

    best_move = (0, 0)
    best_dist = None
    # choose among legal moves the one minimizing distance to target; discourage stepping into obstacles
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        nd = cheb(nx, ny, tx, ty)
        # tie-break by deterministic preference order already encoded in deltas
        if best_dist is None or nd < best_dist:
            best_dist = nd
            best_move = (dx, dy)
    # If all moves were illegal (shouldn't happen), stay
    return [int(best_move[0]), int(best_move[1])]