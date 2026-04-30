def choose_move(observation):
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)
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
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obstacles

    if resources:
        best = None
        best_key = None
        for rx, ry in resources:
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Prefer targets we can beat, then farthest advantage, then closer overall.
            beat = 1 if ds < do else (0 if ds == do else -1)
            # Slightly prefer top-half to avoid mirroring at start; deterministic tie-break.
            center_bias = -abs(rx - (W - 1) / 2) - abs(ry - (H - 1) / 2) * 0.1
            key = (beat, ds - do, ds, -center_bias, rx, ry)
            # Sort order: maximize beat, maximize (do-ds)=-(ds-do), minimize ds; use key crafting above.
            # Convert to comparable: higher beat first, then higher (do-ds), then lower ds.
            score = (beat, -(ds - do), -ds, center_bias, -rx, -ry)
            if best_key is None or score > best_key:
                best_key = score
                best = (rx, ry)
        tx, ty = best
    else:
        tx, ty = (W // 2, H // 2)

    dx_t = 0 if tx == sx else (1 if tx > sx else -1)
    dy_t = 0 if ty == sy else (1 if ty > sy else -1)
    direct = (dx_t, dy_t)

    # Choose best feasible neighbor by local one-step improvement toward target,
    # with anti-blocking (avoid stepping into a cell opponent can reach immediately
    # unless we also reduce our distance more).
    candidates = []
    cur_d = cheb(sx, sy, tx, ty)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        nd = cheb(nx, ny, tx, ty)
        opp_nd = cheb(ox, oy, nx, ny)
        # Prefer reducing distance; prefer moves that also are "safer" vs opponent immediate access.
        improve = cur_d - nd
        key = (improve, -(opp_nd == 1), -(nd), -abs(nx - sx) - abs(ny - sy) * 0.01, dx, dy)
        candidates.append((key, dx, dy, nd))
    if not candidates:
        return [0, 0]

    # If direct is feasible and looks good, bias toward it.
    if direct in [(c[1], c[2]) for c in candidates]:
        best_dxdy = direct
        best_improve = cur_d - cheb(sx + best_dxdy[0], sy + best_dxdy[1], tx, ty)
        # Compare with best candidate.
        best = max(candidates, key=lambda z: z[0])
        if best[0][0] <= best_improve:
            return [best_dxdy[0], best_dxdy[1]]

    _, dx, dy, _ = max(candidates, key=lambda z: z[0])
    return [int(dx), int(dy)]