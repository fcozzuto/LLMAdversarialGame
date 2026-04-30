def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
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

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    # Choose a target resource where we are (potentially) faster than opponent.
    best_t = resources[0]
    best_val = -10**18
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        val = (opd - myd) * 100 - myd
        if (rx, ry) == (sx, sy):
            val += 50
        # Slight bias toward center to reduce pathing dead-ends.
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        val -= int(cheb(rx, ry, cx, cy))
        if val > best_val:
            best_val = val
            best_t = (rx, ry)
    tx, ty = best_t

    deltas = (-1, 0, 1)
    best_move = (0, 0)
    best_move_val = -10**18

    for dx in deltas:
        for dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h):
                continue
            if (nx, ny) in obstacles:
                continue
            myd_next = cheb(nx, ny, tx, ty)
            opd = cheb(ox, oy, tx, ty)
            # Main objective: become closer to target and stay ahead; secondary: avoid giving opponent advantage.
            move_val = (opd - myd_next) * 100 - myd_next
            if (nx, ny) == (sx, sy):
                move_val -= 1  # discourage idle if not needed
            # If we can grab target immediately, strongly prefer it.
            if (nx, ny) == (tx, ty):
                move_val += 10000
            if move_val > best_move_val:
                best_move_val = move_val
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]