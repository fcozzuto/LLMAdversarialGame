def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) == 2:
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

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    # Target choice: maximize advantage (opponent distance - our distance), then prefer closer-to-us.
    best = None
    best_key = None
    for x, y in resources:
        ds = cheb(sx, sy, x, y)
        do = cheb(ox, oy, x, y)
        adv = do - ds
        key = (adv, -ds, x, y)
        if best_key is None or key > best_key:
            best_key = key
            best = (x, y)
    tx, ty = best

    # Candidate moves: prefer the one that reduces our distance to target; break ties by increasing opponent distance.
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    bestm = None
    bestmk = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        ns = cheb(nx, ny, tx, ty)
        no = cheb(ox, oy, tx, ty)
        # Encourage taking resources quickly; if already on target tile, stay is fine.
        key = (-ns, (no - cheb(ox, oy, tx, ty)), -cheb(nx, ny, ox, oy), -abs(nx - tx) - abs(ny - ty), dx, dy)
        if bestmk is None or key > bestmk:
            bestmk = key
            bestm = [dx, dy]

    if bestm is None:
        return [0, 0]
    return [int(bestm[0]), int(bestm[1])]