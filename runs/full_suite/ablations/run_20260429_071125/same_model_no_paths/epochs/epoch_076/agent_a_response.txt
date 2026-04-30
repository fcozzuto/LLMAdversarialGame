def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if inb(x, y):
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not inb(sx, sy):
        dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny):
                return [dx, dy]
        return [0, 0]

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = [0, 0]
    best_val = -10**18

    if resources:
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            my_here = 10**9
            opp_here = 10**9
            val = -10**18
            for rx, ry in resources:
                my_d = cheb(nx, ny, rx, ry)
                op_d = cheb(ox, oy, rx, ry)
                # Prefer targets where we can arrive no later than opponent; otherwise avoid.
                # Small tie-break: prefer closer overall.
                score = (op_d - my_d) * 10 - my_d
                if score > val:
                    val = score
                    my_here, opp_here = my_d, op_d
            # If multiple moves lead to similar target scores, avoid ending closer to opponent than necessary.
            val -= (cheb(nx, ny, ox, oy)) // 3
            if val > best_val:
                best_val = val
                best_move = [dx, dy]
    else:
        # No visible resources: drift toward opponent-avoiding center, but keep deterministic.
        cx, cy = (w - 1) // 2, (h - 1) // 2
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            val = -cheb(nx, ny, cx, cy) - cheb(nx, ny, ox, oy) // 4
            if val > best_val:
                best_val = val
                best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]