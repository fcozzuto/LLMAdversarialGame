def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if free(nx, ny):
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    resources = []
    for r in (observation.get("resources") or []):
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if free(x, y):
                resources.append((x, y))

    cx, cy = (w - 1) // 2, (h - 1) // 2
    best_move = legal[0]
    best_val = -10**18

    # Strategic shift: target resources where we are earlier than opponent; otherwise, contest nearest threatened resource.
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        if resources:
            local_best = -10**18
            for rx, ry in resources:
                dself = cheb(nx, ny, rx, ry)
                dop = cheb(ox, oy, rx, ry)
                # win-like: prefer decreasing our arrival advantage; small bias toward closer absolute distance.
                val = (dop - dself) * 1000 - dself * 2 - cheb(nx, ny, cx, cy) * 0.05
                # If opponent already closer, reduce attraction to that resource unless it's extremely close for us.
                if dself >= dop:
                    val -= (dself - dop) * 200
                local_best = val if val > local_best else local_best
            score = local_best
        else:
            score = -cheb(nx, ny, cx, cy)  # drift to center when no visible resources
            # extra: slightly prefer toward opponent side to avoid being trapped on edges
            score -= cheb(nx, ny, ox, oy) * 0.02
        if score > best_val:
            best_val = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]