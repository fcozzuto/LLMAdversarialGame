def choose_move(observation):
    W = int(observation.get("grid_width") or 8)
    H = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [W - 1, H - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def ok(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if resources:
        best_t = None
        best_val = None
        for tx, ty in resources:
            md = cheb(sx, sy, tx, ty)
            od = cheb(ox, oy, tx, ty)
            # Prefer targets where we are closer than opponent; tie-break toward higher y then x.
            val = (md - od, md, -ty, -tx)
            if best_val is None or val < best_val:
                best_val = val
                best_t = (tx, ty)
        tx, ty = best_t
        # If opponent is also close to this target, nudge toward "contested" side: minimize opponent-to-me distance.
        contested = cheb(ox, oy, tx, ty) <= cheb(sx, sy, tx, ty)
    else:
        tx = (W - 1) // 2
        ty = (H - 1) // 2
        contested = False

    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        # Primary: minimize distance to target
        score = (cheb(nx, ny, tx, ty),)
        if contested:
            # Secondary: if contested, avoid letting opponent reduce our advantage; maximize our distance from opponent.
            score = score + (-cheb(nx, ny, ox, oy),)
        # Tertiary deterministic tie-break: prefer moves that increase x then y (consistently)
        score = score + (-(nx), -(ny))
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]