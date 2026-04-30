def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        resources = [(w // 2, h // 2)]

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    # Target selection: prefer resources where we have a temporal advantage over the opponent.
    best_t = resources[0]
    best_s = -10**9
    for tx, ty in resources:
        ds = cheb(sx, sy, tx, ty)
        do = cheb(ox, oy, tx, ty)
        s = (do - ds) * 1000 - (ds + (w + h) * 0.0)
        # Deterministic tiebreak
        if s > best_s or (s == best_s and (tx, ty) < best_t):
            best_s = s
            best_t = (tx, ty)

    tx, ty = best_t

    # Move selection: minimize our distance to target; if tied, maximize opponent distance to same target.
    chosen = (0, 0)
    chosen_ds = 10**9
    chosen_do = -10**9
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        nds = cheb(nx, ny, tx, ty)
        ndo = cheb(ox, oy, tx, ty)
        # ndo constant for this simple one-step model, keep deterministic tie-break using move order.
        if nds < chosen_ds or (nds == chosen_ds and (ndo > chosen_do)) or (nds == chosen_ds and ndo == chosen_do and (dx, dy) < chosen):
            chosen = (dx, dy)
            chosen_ds = nds
            chosen_do = ndo

    return [int(chosen[0]), int(chosen[1])]