def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        return [0, 0]

    # Choose a resource we can reach no later than the opponent (tie-break by fewer self steps).
    best = None
    best_pair = None  # (self_time - opp_time, self_time, opp_time, resource_index)
    for i, r in enumerate(resources):
        rx, ry = r[0], r[1]
        if not inb(rx, ry):
            continue
        st = cheb(sx, sy, rx, ry)
        ot = cheb(ox, oy, rx, ry)
        # Prefer st <= ot strongly; otherwise avoid.
        gap = st - ot
        if best is None or gap < best_pair[0] or (gap == best_pair[0] and (st < best_pair[1] or (st == best_pair[1] and (ot < best_pair[2] or (ot == best_pair[2] and i < best_pair[3]))))):
            best = (rx, ry)
            best_pair = (gap, st, ot, i)

    if best is None:
        return [0, 0]
    tx, ty = best

    # Greedy step toward target while keeping safe; if opponent is closer, we still try to rush but allow detours around blockers.
    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        ns = cheb(nx, ny, tx, ty)
        no = cheb(nx, ny, ox, oy)
        # Score: primary minimize our distance to target; secondary maximize separation from opponent to avoid them grabbing.
        val = (ns, -no, dx, dy)
        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]