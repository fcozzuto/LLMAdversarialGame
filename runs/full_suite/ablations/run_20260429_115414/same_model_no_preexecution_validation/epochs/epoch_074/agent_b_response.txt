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

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    # Pick a target that is close to us and far from opponent (contested advantage).
    best_t = resources[0]
    best_t_score = None
    for tx, ty in resources:
        ds = cheb(sx, sy, tx, ty)
        do = cheb(ox, oy, tx, ty)
        # Prefer resources where we're closer; slight tie-break to nearer overall.
        score = (do - ds, -(ds + do), -tx, -ty)
        if best_t_score is None or score > best_t_score:
            best_t_score = score
            best_t = (tx, ty)

    tx, ty = best_t

    # Score each candidate move: improve our distance to target, worsen opponent, and avoid stepping away.
    best_move = (0, 0)
    best_score = None
    ds0 = cheb(sx, sy, tx, ty)
    do0 = cheb(ox, oy, tx, ty)
    for dxm, dym in moves:
        nx, ny = sx + dxm, sy + dym
        if not in_bounds(nx, ny):
            nx, ny = sx, sy
            dxm, dym = 0, 0

        ds = cheb(nx, ny, tx, ty)
        do = cheb(ox, oy, tx, ty)  # opponent position fixed this turn

        # Immediate resource pickup bonus: if we land on a resource.
        pickup = 0
        if (nx, ny) in resources:
            pickup = 1000

        # Deterministic tie-break: prefer moves with lower (nx+ny) and then direction order.
        tie = -(nx + ny)

        # Main objective: move toward target, create advantage; also avoid getting stuck by penalizing no progress.
        progress = ds0 - ds
        adv = (do - ds)

        score = (pickup + 10 * adv + 3 * progress, -ds, -cheb(nx, ny, ox, oy), tie, dxm, dym)
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dxm, dym)

    return [int(best_move[0]), int(best_move[1])]