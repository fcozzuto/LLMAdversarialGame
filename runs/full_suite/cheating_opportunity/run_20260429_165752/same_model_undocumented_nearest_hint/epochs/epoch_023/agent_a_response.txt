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

    def inb(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obstacles

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    parity = (sx + sy) & 1

    if not resources:
        tx, ty = (W - 1 + 0) // 2, (H - 1 + 0) // 2
        # If nothing else, drift toward center while staying safe.
        best = (10**9, -10**9, 0, 0)
        bx = syx = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny): 
                continue
            d = cheb(nx, ny, tx, ty)
            k = (d, -(cheb(ox, oy, nx, ny)))
            if k < best[:2]:
                best = (k[0], k[1], nx, ny)
        return [best[2] - sx, best[3] - sy] if best[2] is not None else [0, 0]

    best_t = None
    best_key = None
    for tx, ty in resources:
        ds = cheb(sx, sy, tx, ty)
        do = cheb(ox, oy, tx, ty)
        # Prefer targets where we are strictly earlier than opponent; tie with parity and closeness.
        parity_bonus = 1 if (((tx + ty) & 1) == parity) else 0
        key = (do - ds, parity_bonus, -ds, -(tx + ty))
        if best_key is None or key > best_key:
            best_key = key
            best_t = (tx, ty)

    tx, ty = best_t
    best_move = None
    best_mkey = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        ns = cheb(nx, ny, tx, ty)
        no = cheb(ox, oy, tx, ty)
        # After move: maximize advantage (opponent - self), then reduce distance, then keep parity.
        m_par = 1 if (((nx + ny) & 1) == parity) else 0
        adv = no - ns
        key = (adv, m_par, -ns, -(abs(ox - nx) + abs(oy - ny)))
        if best_mkey is None or key > best_mkey:
            best_mkey = key
            best_move = (dx, dy)

    return list(best_move) if best_move is not None else [0, 0]