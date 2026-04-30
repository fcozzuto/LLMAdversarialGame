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

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        # deterministic retreat/seek based on opponent: go to farthest corner-ish point
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        best = (0, 0)
        bestv = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d = cheb(nx, ny, ox, oy)
            # slight tie-break toward own side (x+y small if we're at bottom-right, etc.)
            corner = corners[((nx + ny) // 2) % 4]
            ta = -cheb(nx, ny, corner[0], corner[1])
            v = 2.0 * d + 0.05 * ta
            if v > bestv:
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    best_move = (0, 0)
    best_val = -10**18

    # Prefer resources where we are closer than opponent; also keep distance from opponent moderately.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d_opp = cheb(nx, ny, ox, oy)
        v = 0.10 * d_opp
        # aggregate by best few resources (deterministic: scan order)
        local_best = -10**18
        for (rx, ry) in resources:
            d_my = cheb(nx, ny, rx, ry)
            d_op = cheb(ox, oy, rx, ry)
            # Want (d_op - d_my) large, and d_my small; penalize giving opponent advantage.
            rel = d_op - d_my
            cur = rel - 0.30 * d_my + (1.6 / (d_my + 1))
            if cur > local_best:
                local_best = cur
        v += local_best
        # tiny deterministic tie-break to reduce dithering
        v += 0.001 * (-(abs(nx - (w - 1)) + abs(ny - (h - 1))))
        if v > best_val:
            best_val = v
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]