def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
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

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if ok(rx, ry):
                resources.append((rx, ry))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    center = ((w - 1) / 2.0, (h - 1) / 2.0)
    remaining = int(observation.get("remaining_resource_count", len(resources)) or 0)
    target_weight = 12.0 if remaining > 0 else 0.0

    best = (0, 0)
    best_val = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        d_op = cheb(nx, ny, ox, oy)
        d_opp_to_next = cheb(ox, oy, nx, ny)

        if resources:
            best_res_gain = -10**18
            for rx, ry in resources:
                myd = cheb(nx, ny, rx, ry)
                od = cheb(ox, oy, rx, ry)
                # Prefer resources we are closer to, otherwise reduce opponent advantage
                gain = (od - myd) - 0.12 * myd
                if gain > best_res_gain:
                    best_res_gain = gain
            val = target_weight * best_res_gain
        else:
            cx, cy = center
            val = -0.25 * cheb(nx, ny, int(cx), int(cy))

        # Mild opponent pressure and keep moving (avoid oscillation by preferring cheb distance change)
        cur_to_op = cheb(sx, sy, ox, oy)
        val += 0.10 * (cur_to_op - d_op)

        # Deterministic tie-break slightly favors moves that progress "toward top-right quadrant"
        # (helps break stalemates consistently)
        prog = 0.001 * (nx - sx + ny - sy) + 0.0001 * (d_op - d_opp_to_next)
        val += prog

        if val > best_val:
            best_val = val
            best = (dx, dy)

    return [int(best[0]), int(best[1])]