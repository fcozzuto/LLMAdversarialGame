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

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def legal(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obstacles

    def step_candidates():
        out = []
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if legal(nx, ny):
                out.append((dx, dy, nx, ny))
        return out

    if not resources:
        return [0, 0]

    # Choose a resource where we are meaningfully closer than the opponent.
    best = None
    best_score = -10**18
    for tx, ty in resources:
        ds = cheb(sx, sy, tx, ty)
        do = cheb(ox, oy, tx, ty)
        # Bias toward winning races; slight preference toward resources nearer the center to avoid corner trapping.
        center_bias = -((tx - (W - 1) / 2.0) ** 2 + (ty - (H - 1) / 2.0) ** 2)
        score = (do - ds) * 100 - ds * 2 + int(center_bias)
        if score > best_score:
            best_score = score
            best = (tx, ty)

    tx, ty = best

    # Move one step to reduce distance to target, while also pushing away from opponent if tie.
    candidates = step_candidates()
    if not candidates:
        return [0, 0]

    best_move = (0, 0)
    best_key = None
    for dx, dy, nx, ny in candidates:
        d_self = cheb(nx, ny, tx, ty)
        d_opp = cheb(nx, ny, ox, oy)
        # Key: smallest distance to target, then largest separation from opponent, then stable tie-break to be deterministic.
        key = (d_self, -d_opp, dx + 2 * dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]