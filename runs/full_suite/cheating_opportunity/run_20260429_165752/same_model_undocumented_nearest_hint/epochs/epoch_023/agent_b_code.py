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
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def legal(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obstacles

    if not resources:
        tx, ty = (W // 2, H // 2)
    else:
        best = None
        best_key = None
        for rx, ry in resources:
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Prefer resources we can reach sooner; then prefer larger advantage; then closer to center.
            center_bias = -cheb(rx, ry, W // 2, H // 2)
            key = (-(do - ds), ds, -center_bias)
            if best_key is None or key < best_key:
                best_key = key
                best = (rx, ry)
        tx, ty = best

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_val = None
    now_ds = cheb(sx, sy, tx, ty)
    now_do = cheb(ox, oy, tx, ty)

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        nds = cheb(nx, ny, tx, ty)
        ndo = now_do  # approximate: our move doesn't change opponent distance directly
        # Strongly reduce our distance; if equal, prefer moves that move us off the opponent's likely line by increasing Cheb to opponent.
        adv = (ndo - nds)
        opp_sep = cheb(nx, ny, ox, oy)
        # Deterministic tie-breaking with coordinates.
        val = (-(adv), nds, -opp_sep, nx, ny)
        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]