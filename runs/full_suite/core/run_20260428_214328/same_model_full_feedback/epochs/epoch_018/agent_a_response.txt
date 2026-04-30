def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def adj_block_pen(x, y):
        pen = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (x + dx, y + dy) in obstacles:
                    pen += 1
        return pen

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
    else:
        # Target resource where we are relatively closer than opponent
        best = None
        best_val = -10**9
        for rx, ry in resources:
            d_me = cheb(sx, sy, rx, ry)
            d_op = cheb(ox, oy, rx, ry)
            # prioritize getting ahead on tempo; slightly prefer nearer absolute to reduce wandering
            val = (d_op - d_me) * 100 - (d_me + d_op)
            if val > best_val or (val == best_val and (rx, ry) < best):
                best_val = val
                best = (rx, ry)
        tx, ty = best

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        d_me = cheb(nx, ny, tx, ty)
        d_op_to_target = cheb(ox, oy, tx, ty)

        # If opponent can reach target very soon, we bias toward interception / alternative
        # Also keep some distance from opponent to avoid losing tempo.
        d_op_me = cheb(nx, ny, ox, oy)
        block_pen = adj_block_pen(nx, ny)

        score = (-d_me * 120) + ((d_op_to_target - d_me) * 40) + (d_op_me * 2) - (block_pen * 6)
        # slight preference for progressing toward target direction
        score += (1 if (abs(tx - nx) < abs(tx - sx) or abs(ty - ny) < abs(ty - sy)) else 0)

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]