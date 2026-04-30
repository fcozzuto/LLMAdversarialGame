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
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def ok(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Choose target resource by (opponent farther than us), then closer to us, then deterministic coords.
    best = None
    best_key = None
    for (x, y) in resources:
        ds = cheb(sx, sy, x, y)
        do = cheb(ox, oy, x, y)
        adv = do - ds
        key = (-adv, ds, x, y)  # minimize -adv => maximize adv; deterministic ties
        if best_key is None or key < best_key:
            best_key = key
            best = (x, y)
    tx, ty = best

    # Greedy one-step: among valid moves, minimize distance to target; break ties by maximizing future advantage vs opponent.
    best_move = (0, 0)
    best_mkey = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d1 = cheb(nx, ny, tx, ty)
        if d1 == 0:
            return [dx, dy]
        # future advantage if we go to (nx,ny) but opponent hasn't moved yet
        do_future = cheb(ox, oy, tx, ty)
        ds_future = d1
        adv_future = do_future - ds_future
        mkey = (d1, -adv_future, nx, ny)
        if best_mkey is None or mkey < best_mkey:
            best_mkey = mkey
            best_move = (dx, dy)

    # Fallback: if somehow all moves invalid, stay.
    return [int(best_move[0]), int(best_move[1])]