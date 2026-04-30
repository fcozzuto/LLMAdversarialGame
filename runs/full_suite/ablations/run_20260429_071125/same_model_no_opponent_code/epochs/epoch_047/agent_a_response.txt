def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [7, 7])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if valid(x, y):
                resources.append((x, y))

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]

    if not valid(sx, sy):
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                return [dx, dy]
        return [0, 0]

    if resources:
        best_res = None
        best_key = None
        for rx, ry in resources:
            md = cheb(sx, sy, rx, ry)
            od = cheb(ox, oy, rx, ry)
            # Prefer resources we can reach earlier (maximize od - md), then closer md, then toward center
            cd = cheb(rx, ry, (w - 1) // 2, (h - 1) // 2)
            key = (od - md, -md, -cd)
            if best_key is None or key > best_key:
                best_key = key
                best_res = (rx, ry)

        rx, ry = best_res
        best_move = (0, 0)
        best_val = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            # Make progress to target; also reduce opponent contest odds
            center_bias = -cheb(nx, ny, (w - 1) // 2, (h - 1) // 2)
            val = (-myd, opd, center_bias, dx, dy)
            if best_val is None or val > best_val:
                best_val = val
                best_move = (dx, dy)
        return [int(best_move[0]), int(best_move[1])]

    # No visible resources: drift toward center while keeping safe
    cx, cy = (w - 1) // 2, (h - 1) // 2
    best_move = (0, 0)
    best_d = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d = cheb(nx, ny, cx, cy)
        if best_d is None or d < best_d or (d == best_d and (dx, dy) < best_move):
            best_d = d
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]