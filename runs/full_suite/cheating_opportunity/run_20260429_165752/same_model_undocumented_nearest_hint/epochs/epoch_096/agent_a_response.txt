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

    def inside(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    cx, cy = (W - 1) / 2.0, (H - 1) / 2.0

    # Target selection: nearest resource by Chebyshev; tie-break toward center.
    if resources:
        tx, ty = min(resources, key=lambda t: (cheb(sx, sy, t[0], t[1]), (t[0] - cx) * (t[0] - cx) + (t[1] - cy) * (t[1] - cy), t[0], t[1]))
    else:
        tx, ty = int(cx), int(cy)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best = (None, -10**18)
    for dxm, dym in moves:
        nx, ny = sx + dxm, sy + dym
        if not inside(nx, ny):
            continue
        d_t = cheb(nx, ny, tx, ty)
        d_o = cheb(nx, ny, ox, oy)
        # If resources exist, prioritize reaching them while keeping some distance from opponent.
        # If no resources, drift toward center while avoiding opponent.
        if resources:
            v = -1.8 * d_t + 0.45 * d_o - 0.02 * ((nx - cx) * (nx - cx) + (ny - cy) * (ny - cy))
        else:
            v = -0.15 * d_t + 0.85 * d_o - 0.02 * ((nx - cx) * (nx - cx) + (ny - cy) * (ny - cy))
        # Deterministic tie-break
        v_key = (v, -abs(dxm), -abs(dym), nx, ny)
        if v_key > (best[1], -10**18, -10**18, -10**18, -10**18):
            best = ((dxm, dym), v_key[0])

    return [int(best[0][0]), int(best[0][1])]