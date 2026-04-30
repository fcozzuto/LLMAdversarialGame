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

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if ok(rx, ry):
                resources.append((rx, ry))

    # If no visible resources, drift toward center away from opponent.
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    best_move = (0, 0)
    best_val = -10**18

    center_w = 0.06
    opp_w = 0.25  # compete for same resource
    safety_w = 0.12  # avoid stepping closer when no good resource

    # Deterministic tie-break: prefer staying still last, so include ordering in evaluation.
    for i, (dx, dy) in enumerate(dirs):
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        base = -0.01 * i  # stable tie-break
        if resources:
            # Choose the best resource to target from this next position.
            # Value = (opponent distance margin) and immediate closeness.
            # Also lightly prefer resources closer to us than opponent.
            best_local = -10**18
            for rx, ry in resources:
                d_self = cheb(nx, ny, rx, ry)
                d_opp = cheb(ox, oy, rx, ry)
                # Higher is better:
                # - prefer smaller self distance
                # - strongly prefer resources where we are closer (d_opp - d_self)
                # - mild penalty if opponent is extremely close too (to avoid immediate fights)
                val = (d_opp - d_self) - 0.55 * d_self - 0.08 * max(0, d_self - 1)
                if val > best_local:
                    best_local = val
            # Add small center preference
            base += best_local + center_w * (-(abs(nx - cx) + abs(ny - cy)))
        else:
            # No resources: keep distance from opponent while going to center.
            base += -safety_w * cheb(nx, ny, ox, oy) + center_w * (-(abs(nx - cx) + abs(ny - cy)))

        if base > best_val:
            best_val = base
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]