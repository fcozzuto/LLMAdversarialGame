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

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

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

    def best_target():
        if not resources:
            return (0 if sx <= (W - 1) // 2 else W - 1, 0 if sy <= (H - 1) // 2 else H - 1)
        best = None
        best_key = None
        for x, y in resources:
            ds = cheb(sx, sy, x, y)
            do = cheb(ox, oy, x, y)
            closer = -1 if ds < do else (0 if ds == do else 1)
            # prefer: we are closer/equal; then smallest distance; then deterministic tie-break
            key = (closer, ds, x, y)
            if best_key is None or key < best_key:
                best_key = key
                best = (x, y)
        return best

    tx, ty = best_target()

    best_move = [0, 0]
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d = cheb(nx, ny, tx, ty)
        # add slight repulsion from opponent to avoid getting trapped near them
        do = cheb(nx, ny, ox, oy)
        val = (d, -do, dx, dy)
        if best_val is None or val < best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move