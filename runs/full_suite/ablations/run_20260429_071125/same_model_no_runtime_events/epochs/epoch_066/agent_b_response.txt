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
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def valid_pos(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]

    def target_value(fromx, fromy):
        best = None
        best_key = None
        for tx, ty in resources:
            ds = cheb(fromx, fromy, tx, ty)
            do = cheb(ox, oy, tx, ty)
            # Prefer targets where we can gain/maintain an edge; lightly penalize if far.
            adv = do - ds
            key = (-(2 * adv - ds), -adv, ds, tx, ty)
            if best_key is None or key < best_key:
                best_key = key
                best = (tx, ty)
        return best_key

    best_move = None
    best_key = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid_pos(nx, ny):
            continue
        k = target_value(nx, ny)
        # If equally good targets, prefer reducing distance to chosen target (implicit in k),
        # then prefer moves that also slightly increase distance from opponent.
        oppd = cheb(nx, ny, ox, oy)
        move_key = (k, -oppd, dx, dy, nx, ny)
        if best_key is None or move_key < best_key:
            best_key = move_key
            best_move = (dx, dy)

    if best_move is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]