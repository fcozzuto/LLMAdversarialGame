def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for b in observation.get("obstacles") or []:
        if b and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                obstacles.add((bx, by))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    # Choose the resource we can reach before (or significantly better than) the opponent.
    if resources:
        best_res = None
        best_res_score = -10**18
        for rx, ry in resources:
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Big bias to being closer than opponent; slight preference for nearer targets.
            score = (do - ds) * 12 - ds
            # If tie, prefer resources nearer to our current position in absolute terms.
            if best_res is None or score > best_res_score:
                best_res_score = score
                best_res = (rx, ry)
        tx, ty = best_res
    else:
        # No visible resources: fall back to staying safe and drifting toward opponent's side.
        tx, ty = (w - 1, h - 1) if (sx + sy) < (ox + oy) else (0, 0)

    # Evaluate each move by improving the gap to the chosen target after the move.
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        ds_after = cheb(nx, ny, tx, ty)
        do_after = cheb(ox, oy, tx, ty)
        gap = (do_after - ds_after) * 12
        # Secondary objective: keep some distance from opponent unless it helps capture.
        safety = -cheb(nx, ny, ox, oy)
        # Tiny tie-break to move toward the target.
        forward = - (abs(nx - tx) + abs(ny - ty)) * 0.01
        val = gap + safety + forward
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]