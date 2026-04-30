def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if resources:
        best_move = (0, 0)
        best_val = 10**18
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                nx, ny = sx, sy
            # Evaluate by best (most stealable) target after this move
            val = 10**18
            for rx, ry in resources:
                d_self = cheb(nx, ny, rx, ry)
                d_opp = cheb(ox, oy, rx, ry)
                # Prefer resources we're closer to; penalize ones opponent is nearer to
                cur = d_self - 0.65 * d_opp
                # Tiny tie-breaker to move toward center of resources spread
                cur += 0.01 * (abs(rx - (w - 1) / 2) + abs(ry - (h - 1) / 2)) * 0.0
                if cur < val:
                    val = cur
            # Tie-break: prefer smaller distance to the single best target from current pos
            tie = None
            if resources:
                # deterministic: pick closest to (nx,ny) in cheb, then smallest coords
                min_d = 10**9
                target = None
                for rx, ry in resources:
                    d = cheb(nx, ny, rx, ry)
                    if d < min_d or (d == min_d and (rx, ry) < target):
                        min_d = d
                        target = (rx, ry)
                tie = (min_d, target[0], target[1])
            if val < best_val or (val == best_val and tie < (0, 0, 0)):
                best_val = val
                best_move = (dx, dy)
        return [int(best_move[0]), int(best_move[1])]

    # No visible resources: drift to a central point, but keep obstacle safety
    tx, ty = (w - 1) // 2, (h - 1) // 2
    bestd = 10**9
    bestm = (0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            nx, ny = sx, sy
        d = cheb(nx, ny, tx, ty)
        if d < bestd or (d == bestd and (dx, dy) < bestm):
            bestd = d
            bestm = (dx, dy)
    return [int(bestm[0]), int(bestm[1])]