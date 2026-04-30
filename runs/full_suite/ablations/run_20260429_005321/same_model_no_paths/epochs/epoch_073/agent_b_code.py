def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
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

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    if not valid(sx, sy):
        sx = 0 if sx < 0 else (w - 1 if sx >= w else sx)
        sy = 0 if sy < 0 else (h - 1 if sy >= h else sy)

    moves = []
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                moves.append((dx, dy))
    if not moves:
        return [0, 0]

    best_move = None
    best_val = None
    for dx, dy in moves:
        nsx, nsy = sx + dx, sy + dy
        best_for_move = None
        for rx, ry in resources:
            ds = cheb(nsx, nsy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Prefer resources we can reach first; break ties by being closer.
            val = (do - ds) * 10 - ds
            if best_for_move is None or val > best_for_move:
                best_for_move = val
        # Small deterministic tie-breaker: prefer staying still less? use fixed order via dx,dy magnitude.
        tie = (abs(dx) + abs(dy), dx, dy)
        if best_val is None or best_for_move > best_val or (best_for_move == best_val and tie < (abs(best_move[0]) + abs(best_move[1]), best_move[0], best_move[1])):
            best_val = best_for_move
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]