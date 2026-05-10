def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", (0, 0))
    op = observation.get("opponent_position", (w - 1, h - 1))
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                resources.append((x, y))

    if resources:
        best = None
        best_key = None
        for x, y in resources:
            dS = cheb(sx, sy, x, y)
            dO = cheb(ox, oy, x, y)
            score = dS - dO  # prefer being closer than opponent
            # small bias toward nearer resources and deterministic tie-break by position
            key = (score, dS, x, y)
            if best_key is None or key < best_key:
                best_key = key
                best = (x, y)

        tx, ty = best
        candidates = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
        best2 = None
        best2_key = None
        for dx, dy in candidates:
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in blocked:
                continue
            # race advantage after move
            ndS = cheb(nx, ny, tx, ty)
            ndO = cheb(ox, oy, tx, ty)
            # also gently avoid stepping away overall
            key = (ndS - ndO, ndS, abs(nx - tx) + abs(ny - ty), dx, dy)
            if best2_key is None or key < best2_key:
                best2_key = key
                best2 = (dx, dy)
        if best2 is not None:
            return [int(best2[0]), int(best2[1])]

    # fallback: drift toward center/right depending on parity (deterministic)
    target_x = (w - 1) if (sy % 2 == 0) else 0
    target_y = h // 2
    dx = 0
    if sx < target_x:
        dx = 1
    elif sx > target_x:
        dx = -1
    dy = 0
    if sy < target_y:
        dy = 1
    elif sy > target_y:
        dy = -1
    return [int(dx), int(dy)]