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

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def inb(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obstacles
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny):
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def pick_target():
        if not resources:
            return None
        best = None
        best_key = None
        for i, (rx, ry) in enumerate(resources):
            sd = cheb(sx, sy, rx, ry)
            od = cheb(ox, oy, rx, ry)
            # Prefer resources we can be at least as fast for; tie-break by closeness and determinism
            key = (-(od - sd), sd, i)
            if best_key is None or key < best_key:
                best_key = key
                best = (rx, ry)
        return best

    target = pick_target()

    # If no resources visible, keep distance from opponent while staying safe
    if target is None:
        best = None
        best_val = None
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            v = cheb(nx, ny, ox, oy)  # maximize opponent distance
            key = (-v, dx, dy)
            if best_val is None or key < best_val:
                best_val = key
                best = (dx, dy)
        return [int(best[0]), int(best[1])]

    tx, ty = target
    # Choose move that reduces distance to target; if tie, prefer moves that reduce opponent access
    best = None
    best_key = None
    cur_sd = cheb(sx, sy, tx, ty)
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        nsd = cheb(nx, ny, tx, ty)
        nod = cheb(ox, oy, tx, ty)
        # Opponent distance is static here; use our new distance plus a slight bias to keep away from opponent
        new_opp = cheb(nx, ny, ox, oy)
        improve = cur_sd - nsd
        key = (-improve, nsd, -(new_opp), dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best = (dx, dy)
    return [int(best[0]), int(best[1])]