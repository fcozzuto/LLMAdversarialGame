def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for b in observation.get("obstacles") or []:
        if b and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                obstacles.add((bx, by))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))

    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    # Deterministic tie-break: prefer staying/straight moves toward goal-ish directions
    moves = [(-1, 0), (0, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1)]

    def value_target(rx, ry, myx, myy):
        ds = cheb(myx, myy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # High priority: deny opponent by arriving first (margin do-ds)
        margin = do - ds
        # Proxy for resource "importance": prefer farther from (0,0) and edges slightly, deterministic
        proxy = (rx + ry) + 0.1 * (w - 1 - rx + h - 1 - ry)
        return margin * 1000 - ds * 3 + proxy

    # Also compute opponent's current best target, to reduce their advantage
    opp_best = None
    opp_best_score = -10**18
    for rx, ry in resources:
        sc = cheb(ox, oy, rx, ry)  # smaller is better, used for ordering
        if opp_best is None or sc < opp_best_score:
            opp_best = (rx, ry)
            opp_best_score = sc

    best_move = (0, 0)
    best_eval = -10**18

    for mdx, mdy in moves:
        nx, ny = sx + mdx, sy + mdy
        if not inb(nx, ny):
            continue

        # Evaluate by choosing our best target after this move
        my_best = None
        my_best_score = -10**18
        for rx, ry in resources:
            sc = value_target(rx, ry, nx, ny)
            if sc > my_best_score:
                my_best_score = sc
                my_best = (rx, ry)

        # If we can deny opponent's current best target, reward it
        deny = 0
        if opp_best is not None:
            rx, ry = opp_best
            deny = (cheb(ox, oy, rx, ry) - cheb(nx, ny, rx, ry)) * 500

        # Small tie-break: prefer moving closer to center
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        dist_center = cheb(nx, ny, cx, cy) if True else 0

        eval_score = my_best_score + deny - dist_center * 0.01

        if eval_score > best_eval:
            best_eval = eval_score
            best_move = (mdx, mdy)

    return [int(best_move[0]), int(best_move[1])]