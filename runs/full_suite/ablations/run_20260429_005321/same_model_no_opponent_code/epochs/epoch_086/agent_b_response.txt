def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
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

    def cheb(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                return [dx, dy]
        return [0, 0]

    # Pick a target resource likely to stay "ours": close to us, far from opponent.
    def target_for(cx, cy):
        best = None
        best_val = -10**9
        for rx, ry in resources:
            v = -cheb(cx, cy, rx, ry) + 0.6 * cheb(ox, oy, rx, ry)
            # tie-break deterministically toward lower x then lower y
            if v > best_val or (v == best_val and (best is None or (rx, ry) < best)):
                best_val = v
                best = (rx, ry)
        return best

    target = target_for(sx, sy)
    if target is None:
        return [0, 0]
    tx, ty = target

    best_move = [0, 0]
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        # Recompute best local target after the move (keeps policy responsive).
        t2 = target_for(nx, ny)
        if t2 is None:
            t2 = (tx, ty)
        tx2, ty2 = t2

        d = cheb(nx, ny, tx2, ty2)
        do = cheb(nx, ny, ox, oy)

        # Encourage progress and keep distance from opponent; slight penalty for closer-to-opponent target.
        score = (-2.2 * d) + (0.35 * do) - (0.08 * cheb(ox, oy, tx2, ty2))

        # Deterministic tie-break: prefer moves with smaller (dx,dy) order in moves list
        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move