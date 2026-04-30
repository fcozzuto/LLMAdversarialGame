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

    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    best = None
    best_pr = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        pr = (do - ds) * 4 - ds  # prefer targets opponent is farther from, then closeness
        if best is None or pr > best_pr or (pr == best_pr and (rx, ry) < best):
            best_pr = pr
            best = (rx, ry)

    tx, ty = best
    if sx == tx and sy == ty:
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = None
    best_dist = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        dist = cheb(nx, ny, tx, ty)
        if best_move is None or dist < best_dist:
            best_move = [dx, dy]
            best_dist = dist
        elif dist == best_dist:
            # deterministic tie-break: prefer moves that also make us not too far from target along x then y
            if (abs((sx + dx) - tx), abs((sy + dy) - ty), dx, dy) < (abs((sx + best_move[0]) - tx), abs((sy + best_move[1]) - ty), best_move[0], best_move[1]):
                best_move = [dx, dy]

    return best_move if best_move is not None else [0, 0]