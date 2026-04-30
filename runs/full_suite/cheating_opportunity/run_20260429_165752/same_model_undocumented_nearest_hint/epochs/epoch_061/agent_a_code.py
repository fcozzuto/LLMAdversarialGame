def choose_move(observation):
    W = int(observation.get("grid_width", 8))
    H = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [W - 1, H - 1])
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

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def legal(nx, ny):
        return 0 <= nx < W and 0 <= ny < H and (nx, ny) not in obstacles

    def score_target(tx, ty):
        ds = cheb(sx, sy, tx, ty)
        do = cheb(ox, oy, tx, ty)
        return (ds - do, ds, -(tx - ty), tx, ty)

    if not resources:
        # Drift to increase distance from opponent, while not stepping into obstacles.
        best = None
        best_move = (0, 0)
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            dso = cheb(nx, ny, ox, oy)
            t = (-dso, dx, dy)
            if best is None or t < best:
                best = t
                best_move = (dx, dy)
        return [best_move[0], best_move[1]]

    # Choose target that we can reach first (minimize ds-do), deterministic tie breaks.
    best_t = None
    tx, ty = resources[0]
    for r in resources:
        s = score_target(r[0], r[1])
        if best_t is None or s < best_t:
            best_t = s
            tx, ty = r

    # Take a step that maximizes our progress to target and minimizes giving opponent advantage.
    best = None
    best_move = (0, 0)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        ds_new = cheb(nx, ny, tx, ty)
        do_new = cheb(ox, oy, tx, ty)
        # Prefer smaller ds_new, then larger distance from opponent, then stable tie by position.
        t = (ds_new - do_new, ds_new, -cheb(nx, ny, ox, oy), nx, ny, dx, dy)
        if best is None or t < best:
            best = t
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]