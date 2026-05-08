def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obstacles.add((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if inb(x, y):
                resources.append((x, y))

    if not resources:
        return [0, 0]

    best = None
    best_score = None
    for tx, ty in resources:
        ds = cheb(sx, sy, tx, ty)
        do = cheb(ox, oy, tx, ty)
        score = ds - 0.6 * do  # prioritize resources opponent is less able to reach
        if best_score is None or score < best_score or (score == best_score and (tx, ty) < best):
            best_score = score
            best = (tx, ty)
    tx, ty = best

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cur_dist = cheb(sx, sy, tx, ty)
    chosen = (0, 0)
    chosen_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        nd = cheb(nx, ny, tx, ty)
        # prefer moves that reduce distance; then deny by maximizing opponent distance after our move
        opp_after = cheb(ox, oy, tx, ty)
        key = (nd - nd, 0)  # placeholder to keep tuple shape; overwritten below
        key = (nd, -opp_after, abs(nx - tx) + abs(ny - ty), (dx, dy))
        if chosen_key is None or key < chosen_key:
            chosen_key = key
            chosen = (dx, dy)
        if nd < cur_dist:
            # early accept best-looking improving move deterministically by continuing tie logic
            pass

    return [int(chosen[0]), int(chosen[1])]