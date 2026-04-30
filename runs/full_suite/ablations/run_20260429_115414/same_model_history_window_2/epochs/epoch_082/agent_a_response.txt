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

    res = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in blocked:
                res.append((rx, ry))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    cx, cy = w // 2, h // 2

    best_mv = (0, 0)
    best_sc = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            sc = -10**12
        else:
            if res:
                # contest resources: prefer becoming closer than opponent; add center bias for tie-breaking
                sc = 0
                best = -10**18
                for rx, ry in res:
                    d_me = cheb(nx, ny, rx, ry)
                    d_op = cheb(ox, oy, rx, ry)
                    # Strongly reward resources where we are already closer (or can be)
                    gain = d_op - d_me
                    # Reduce penalty for distance; slightly prefer nearer resources generally
                    val = 8 * gain - d_me + 0.02 * (-(cheb(nx, ny, cx, cy)))
                    if val > best:
                        best = val
                sc = best
                # If we would be blocked from the best area next turn, discourage by mild distance sum
                sc += -0.01 * cheb(nx, ny, ox, oy)
            else:
                # No visible resources: go to center while keeping distance from opponent
                sc = -cheb(nx, ny, cx, cy) - 0.05 * cheb(nx, ny, ox, oy)
        if sc > best_sc:
            best_sc = sc
            best_mv = (dx, dy)

    return [int(best_mv[0]), int(best_mv[1])]