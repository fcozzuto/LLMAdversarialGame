def choose_move(observation):
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)

    obstacles = set()
    for o in observation.get("obstacles", []) or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            obstacles.add((int(o[0]), int(o[1])))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    # Pick a resource that we can reach early but where the opponent is relatively slower.
    best_t = None
    best_score = -10**18
    for tx, ty in resources:
        ds = cheb(sx, sy, tx, ty)
        do = cheb(ox, oy, tx, ty)
        # Prefer winning races: maximize (opponent_slowdown) minus our distance.
        score = (do - ds) * 5 - ds
        if score > best_score:
            best_score = score
            best_t = (tx, ty)

    tx, ty = best_t
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obstacles:
            continue
        ds2 = cheb(nx, ny, tx, ty)
        # Keep separation to avoid direct contests; also avoid stepping onto the opponent.
        sep = cheb(nx, ny, ox, oy)
        opp_pen = 0 if sep > 1 else (3 - sep) * 4
        # Small tie-break: prefer progressing upward in our race.
        val = -ds2 * 10 + sep - opp_pen
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]