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

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in blocked:
                resources.append((rx, ry))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def dist_cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if resources:
        best_move = (0, 0)
        best_val = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            score = -10**18
            # Score move by best "capture advantage" among visible resources
            for rx, ry in resources:
                ds = dist_cheb(nx, ny, rx, ry)
                do = dist_cheb(ox, oy, rx, ry)
                # Prefer moves that make us strictly closer to a resource than opponent
                val = (do - ds) * 1000 - ds
                if (rx == nx and ry == ny):
                    val += 10**6
                if val > score:
                    score = val
            # Slight tie-break: prefer closer to opponent to block? actually maximize our advantage first
            tie = dist_cheb(nx, ny, ox, oy)
            val2 = score - tie * 0.001
            if val2 > best_val:
                best_val = val2
                best_move = (dx, dy)
        return [int(best_move[0]), int(best_move[1])]

    # No visible resources: keep mobility while maximizing distance from opponent
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        far = dist_cheb(nx, ny, ox, oy)
        stay_pen = 0 if (dx != 0 or dy != 0) else 0.01
        val = far - stay_pen
        if val > best_val:
            best_val = val
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]