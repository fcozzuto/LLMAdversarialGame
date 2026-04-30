def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for b in observation.get("obstacles") or []:
        if b and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                blocked.add((bx, by))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if ok(rx, ry):
                resources.append((rx, ry))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if ok(nx, ny):
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    def best_target(px, py):
        if not resources:
            return None, 10**9
        best_r = None
        best_key = None
        for rx, ry in resources:
            ds = cheb(px, py, rx, ry)
            do = cheb(ox, oy, rx, ry)
            adv = do - ds  # positive means we are closer than opponent
            key = (-adv, ds, rx, ry)  # maximize adv, then minimize ds
            if best_key is None or key < best_key:
                best_key = key
                best_r = (rx, ry)
        # Convert to an advantage score for comparison
        rx, ry = best_r
        ds = cheb(px, py, rx, ry)
        do = cheb(ox, oy, rx, ry)
        return best_r, (do - ds)

    best_move = None
    best_score = -10**18
    for dx, dy, nx, ny in legal:
        # Avoid walking into opponent "capture" vicinity when resources are scarce
        opp_d = cheb(nx, ny, ox, oy)
        danger = 0
        if opp_d <= 1:
            danger = 3 - opp_d  # 2 or 3

        target, adv = best_target(nx, ny)
        if target is None:
            # Simple drift to center if no resources visible
            cx, cy = (w - 1) // 2, (h - 1) // 2
            ds = cheb(nx, ny, cx, cy)
            score = -ds - 0.5 * danger
        else:
            # Prefer gaining advantage and reducing distance to the chosen target
            rx, ry = target
            ds = cheb(nx, ny, rx, ry)
            score = 8 * adv - 1.2 * ds - 0.8 * danger

        if score > best_score or (score == best_score and (best_move is None or (dx, dy) < (best_move[0], best_move[1]))):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]