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
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def legal(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obstacles

    def mobility(x, y):
        c = 0
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if legal(nx, ny):
                c += 1
        return c

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not resources:
        tx, ty = W // 2, H // 2
        best = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            v = -cheb(nx, ny, tx, ty) + 0.05 * mobility(nx, ny)
            if best is None or v > best[0] or (v == best[0] and (nx, ny) < best[1]):
                best = (v, (nx, ny), (dx, dy))
        return best[2]

    res_list = sorted(resources)[:10]  # deterministic cap
    bestv = None
    bestmove = (0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        # Score targets by resulting advantage (opponent farther than us) and closeness.
        mv = -10**9
        for tx, ty in res_list:
            ds = cheb(nx, ny, tx, ty)
            do = cheb(ox, oy, tx, ty)
            # Prefer taking resources (ds=0) and swing the lead; discourage being "stuck" near obstacles.
            base = (do - ds) * 20
            take = 200 if ds == 0 else 0
            tie = -ds
            mob = mobility(nx, ny) * 2
            # Mild anti-rug: if move reduces mobility a lot, penalize.
            mv = max(mv, base + take + tie + mob - (4 - mob))
        # Extra penalty if landing adjacent to many obstacles (risk of trapping).
        adj_obs = 0
        for adx, ady in [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)]:
            ax, ay = nx + adx, ny + ady
            if (ax, ay) in obstacles:
                adj_obs += 1
        v = mv - adj_obs * 3
        if bestv is None or v > bestv or (v == bestv and (nx, ny) < (sx + bestmove[0], sy + bestmove[1])):
            bestv = v
            bestmove = (dx, dy)
    return [int(bestmove[0]), int(bestmove[1])]