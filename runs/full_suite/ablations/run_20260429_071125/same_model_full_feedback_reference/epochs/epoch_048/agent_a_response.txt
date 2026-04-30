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

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if ok(x, y):
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not ok(sx, sy):
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if ok(nx, ny):
                return [int(dx), int(dy)]
        return [0, 0]

    # Choose best target: maximize (opp_dist - self_dist) with deterministic tie-breaks.
    if resources:
        best = None
        best_key = None
        for tx, ty in resources:
            sd = cheb(sx, sy, tx, ty)
            od = cheb(ox, oy, tx, ty)
            # Prefer reaching earlier and preventing opponent priority.
            key = (od - sd, -sd, od, tx, ty)
            if best_key is None or key > best_key:
                best_key = key
                best = (tx, ty)
        tx, ty = best
    else:
        # Fallback: head toward the center-ish point deterministically.
        tx, ty = w // 2, h // 2

    # Evaluate one-step moves toward target; prefer safer and more "winning" margin after the move.
    best_move = (0, 0)
    best_key = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        self_after = cheb(nx, ny, tx, ty)
        opp_margin = cheb(ox, oy, tx, ty) - self_after
        # Safety: avoid moving adjacent to obstacles if it doesn't hurt margin.
        adj_obs = 0
        for ax, ay in [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]:
            if (nx + ax, ny + ay) in obstacles:
                adj_obs += 1
        # Tie-break deterministically by direction preference order.
        dir_idx = dirs.index((dx, dy))
        key = (opp_margin, -self_after, -adj_obs, -abs((nx - tx)) - abs((ny - ty)), -dir_idx)
        if best_key is None or key > best_key:
            best_key = key
            best_move = (dx, dy)

    dx, dy = best_move
    return [int(dx), int(dy)]