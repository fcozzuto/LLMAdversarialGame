def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [w - 1, h - 1]) or [w - 1, h - 1]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
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

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    # Target: maximize advantage = (opponent distance - our distance), tie-break by our distance (closer)
    best_t = resources[0]
    best_adv = None
    best_ds = None
    for tx, ty in resources:
        ds = cheb(sx, sy, tx, ty)
        do = cheb(ox, oy, tx, ty)
        adv = do - ds
        if best_adv is None or adv > best_adv or (adv == best_adv and ds < best_ds):
            best_adv = adv
            best_ds = ds
            best_t = (tx, ty)

    tx, ty = best_t

    deltas = []
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            deltas.append((dx, dy))

    # If very close to target, prefer holding position or next best to avoid wasting move
    near = cheb(sx, sy, tx, ty) <= 1

    best_move = (0, 0)
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d_to = cheb(nx, ny, tx, ty)
        d_opp = cheb(ox, oy, tx, ty)
        step_adv = d_opp - d_to  # higher is better
        # Penalize getting stuck near obstacles: count adjacent obstacle cells
        adj = 0
        for ady in (-1, 0, 1):
            for adx in (-1, 0, 1):
                if adx == 0 and ady == 0:
                    continue
                axp, ayp = nx + adx, ny + ady
                if (axp, ayp) in obstacles:
                    adj += 1
        score = (step_adv, -d_to, -adj, -1 if (near and dx == 0 and dy == 0) else 0)
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]