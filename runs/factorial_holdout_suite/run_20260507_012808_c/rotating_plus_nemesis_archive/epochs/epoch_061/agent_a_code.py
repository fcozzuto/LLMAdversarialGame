def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    ox, oy = observation.get("opponent_position") or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

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
            if 0 <= x < w and 0 <= y < h:
                resources.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def pick_target():
        best = None
        bestk = None
        for x, y in resources:
            ds = cheb(sx, sy, x, y)
            do = cheb(ox, oy, x, y)
            # Prefer resources we can reach sooner; otherwise steal chances.
            k = (do - ds, -ds, -do, x, y)
            if bestk is None or k > bestk:
                bestk = k
                best = (x, y)
        return best

    target = pick_target()
    if not target:
        return [0, 0]
    tx, ty = target

    # Try to step toward target with obstacle avoidance.
    best_move = None
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        ds_next = cheb(nx, ny, tx, ty)
        # If opponent is very close, prioritize reducing our distance to target.
        do_now = cheb(ox, oy, tx, ty)
        score = (-ds_next, -abs((do_now - ds_next)), -nx, -ny)
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    if best_move is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]