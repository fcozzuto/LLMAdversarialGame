def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for b in observation.get("obstacles") or []:
        if isinstance(b, (list, tuple)) and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                obstacles.add((bx, by))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))

    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    opp_here = (ox, oy)
    best = None
    best_key = None
    for rx, ry in resources:
        if (rx, ry) == opp_here:
            continue
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        win = 0 if sd <= od else 1  # prefer resources we can reach first
        # Tie-break: smaller sd, then prefer more "edge" targets to reduce opponent sweep opportunities
        edge_bias = -min(rx, w - 1 - rx) - min(ry, h - 1 - ry)
        key = (win, sd - od, sd, edge_bias)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    if best is None:
        rx, ry = resources[0]
    else:
        rx, ry = best

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    # Deterministic tie-breaking order: keep original order and minimize a tuple
    best_move = None
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        dist = cheb(nx, ny, rx, ry)
        hit_res = 1 if (nx, ny) == (rx, ry) else 0
        score = (-hit_res, dist, abs(dx) + abs(dy), dx, dy)
        if best_score is None or score < best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move if best_move is not None else [0, 0]