def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
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

    def best_target(px, py):
        best = None
        for tx, ty in resources:
            if (tx, ty) in obstacles:
                continue
            sd = cheb(px, py, tx, ty)
            od = cheb(ox, oy, tx, ty)
            # Prefer: win resource (sd<od), then minimize our distance, then prevent opponent closer, then deterministic.
            key = (0 if sd < od else 1, sd, -od, tx, ty)
            if best is None or key < best[0]:
                best = (key, (tx, ty))
        return best[1]

    tx, ty = best_target(sx, sy)

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if nx < 0: nx = 0
            if nx >= w: nx = w - 1
            if ny < 0: ny = 0
            if ny >= h: ny = h - 1
            if (nx, ny) in obstacles:
                continue
            # If step on/near a target, prefer reducing opponent lead; deterministic tie-break.
            ns = cheb(nx, ny, tx, ty)
            os = cheb(ox, oy, tx, ty)
            score_key = (0 if ns < os else 1, ns, cheb(nx, ny, ox, oy), dx, dy)
            moves.append((score_key, [dx, dy]))
    if not moves:
        return [0, 0]
    moves.sort(key=lambda t: t[0])
    return moves[0][1]