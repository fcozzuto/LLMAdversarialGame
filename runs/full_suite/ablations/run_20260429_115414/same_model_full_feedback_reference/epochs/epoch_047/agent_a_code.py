def choose_move(observation):
    W = int(observation.get("grid_width") or 8)
    H = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [W - 1, H - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obstacles

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        best = None
        best_score = None
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny): 
                continue
            sc = -(cheb(nx, ny, ox, oy))  # drift away from opponent when no resources visible
            if best_score is None or sc > best_score:
                best_score, best = sc, [dx, dy]
        return best if best is not None else [0, 0]

    # If standing on a resource, stay.
    for rx, ry in resources:
        if rx == sx and ry == sy:
            return [0, 0]

    # Score moves by best available target where we account for opponent contention.
    best_move = [0, 0]
    best_sc = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        move_sc = -10**9
        for rx, ry in resources:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            # Prefer targets we can reach sooner than opponent; otherwise pick still-valuable near ones.
            # Also slightly prefer targets that are closer overall.
            cont = opd - myd
            sc = (cont * 3) - myd - (cheb(nx, ny, rx, ry) > 0) * 0.1
            if sc > move_sc:
                move_sc = sc
        # Small tie-break: keep moving closer to current best target direction deterministically.
        tie = cheb(nx, ny, resources[0][0], resources[0][1])
        total = move_sc - 0.01 * tie
        if best_sc is None or total > best_sc:
            best_sc = total
            best_move = [dx, dy]

    return best_move