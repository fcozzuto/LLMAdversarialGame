def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))
    resources = observation.get("resources") or []

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def move_order():
        return [(-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1), (0, 0)]

    # If no resources, head to center deterministically.
    if not resources:
        tx, ty = w // 2, h // 2
    else:
        # Target a resource that we can reach earlier (or deny): minimize (my - opp), then my distance, then tie by coordinates.
        best = None
        for rx, ry in resources:
            md = cheb(sx, sy, rx, ry)
            od = cheb(ox, oy, rx, ry)
            score_key = (md - od, md, rx, ry)
            if best is None or score_key < best[0]:
                best = (score_key, (rx, ry))
        tx, ty = best[1]

    curd = cheb(sx, sy, tx, ty)
    best_move = None
    best_key = None
    # Greedy step toward target; tie-break by improving our advantage vs opponent at next positions.
    for dx, dy in move_order():
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        nd = cheb(nx, ny, tx, ty)
        # Advantage if we get closer than opponent gets to the same target.
        adv = (cheb(ox, oy, tx, ty) - nd)
        # Also include whether the move reduces distance strictly.
        key = (nd - curd, -adv, nx, ny)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    if best_move is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]