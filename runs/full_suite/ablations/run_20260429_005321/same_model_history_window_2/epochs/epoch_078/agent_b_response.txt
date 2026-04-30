def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
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

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources:
        tx, ty = w // 2, h // 2
    else:
        best = None
        best_key = None
        for rx, ry in resources:
            d_me = cheb(sx, sy, rx, ry)
            d_op = cheb(ox, oy, rx, ry)
            # Prefer resources we can reach sooner; break ties by keeping opponent far.
            key = (d_me, -d_op, rx, ry)
            if best_key is None or key < best_key:
                best_key = key
                best = (rx, ry)
        tx, ty = best

        # If opponent is much closer, pick a different resource to deny them.
        d_me = cheb(sx, sy, tx, ty)
        d_op = cheb(ox, oy, tx, ty)
        if d_op + 1 < d_me and len(resources) > 1:
            best2 = None
            best2_key = None
            for rx, ry in resources:
                d_me2 = cheb(sx, sy, rx, ry)
                d_op2 = cheb(ox, oy, rx, ry)
                # Prefer smaller (our distance) but also larger (opponent distance)
                key = (d_me2, -d_op2, rx, ry)
                if best2_key is None or key < best2_key:
                    best2_key = key
                    best2 = (rx, ry)
            tx, ty = best2

    # Choose move by one-step evaluation: closer to target, and farther from opponent's position.
    # Also lightly avoid stepping into adjacent squares of opponent.
    best_move = (0, 0)
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        dist_to_target = cheb(nx, ny, tx, ty)
        dist_opp = cheb(nx, ny, ox, oy)
        # adjacency penalty if we move next to opponent (discourage easy contest)
        adj_pen = 1 if dist_opp == 1 else 0
        # keep opponent from reaching target: maximize opponent-target distance after our move (approx)
        opp_target = cheb(ox, oy, tx, ty)
        # opponent-target doesn't change, so only use a small tie-break based on our distance advantage
        advantage = (cheb(ox, oy, tx, ty) - cheb(nx, ny, tx, ty))
        val_key = (dist_to_target, adj_pen, -dist_opp, -advantage, nx, ny)
        if best_val is None or val_key < best_val:
            best_val = val_key
            best_move = (dx, dy)

    dx, dy = best_move
    return [dx, dy]