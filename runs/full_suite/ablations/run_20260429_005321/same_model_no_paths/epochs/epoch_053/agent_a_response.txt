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

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    deltas = moves

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def mobility(x, y):
        c = 0
        for dx, dy in deltas:
            nx, ny = x + dx, y + dy
            if inside(nx, ny):
                c += 1
        return c

    if not resources:
        return [0, 0]

    best_move = [0, 0]
    best_val = -10**9

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        mob = mobility(nx, ny)
        if (nx, ny) in obstacles:
            continue

        # Target resource by "pressure": where we can arrive earlier than opponent.
        # If we can't beat them, move toward a still-hard-to-reach resource.
        target_score = -10**9
        for rx, ry in resources:
            d_self = cheb(nx, ny, rx, ry)
            d_opp = cheb(ox, oy, rx, ry)
            beat = d_opp - d_self  # positive means we are closer now (or can reach first next)
            # small tie-break to reduce pathing issues: prefer nearer resource and good mobility
            s = beat * 10 - d_self * 0.8
            if s > target_score:
                target_score = s

        # Obstacle handling: avoid positions with low mobility (potential local trapping).
        val = target_score + mob * 1.6
        # Also discourage moving adjacent to obstacles unless it also improves pressure.
        adj = 0
        for ox2, oy2 in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            if inside(nx + ox2, ny + oy2) is False and (nx + ox2, ny + oy2) in obstacles:
                adj += 1
        val -= adj * 0.8

        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]