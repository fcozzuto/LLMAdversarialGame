def choose_move(observation):
    W = observation.get("grid_width", 0)
    H = observation.get("grid_height", 0)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))

    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            t = (p[0], p[1])
            if t not in obs:
                res.append(t)

    def inb(x, y):
        return 0 <= x < W and 0 <= y < H

    def legal(x, y):
        return inb(x, y) and (x, y) not in obs

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    best = (0, 0)
    bestv = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        if res:
            v = -10**18
            for rx, ry in res:
                my_d = cheb(nx, ny, rx, ry)
                op_d = cheb(ox, oy, rx, ry)
                gain = (op_d - my_d) - 0.2 * my_d
                if nx == rx and ny == ry:
                    gain += 8.0
                if gain > v:
                    v = gain
        else:
            # No known resources: move to keep distance from opponent while drifting toward center.
            my_d = cheb(nx, ny, (W - 1) // 2, (H - 1) // 2)
            op_d = cheb(nx, ny, ox, oy)
            v = 0.3 * op_d - 0.05 * my_d
        if v > bestv:
            bestv = v
            best = (dx, dy)
        elif v == bestv:
            # deterministic tie-break: prefer smaller move magnitude, then dx, then dy
            curm = abs(best[0]) + abs(best[1])
            nm = abs(dx) + abs(dy)
            if nm < curm or (nm == curm and (dx < best[0] or (dx == best[0] and dy < best[1]))):
                best = (dx, dy)

    return [int(best[0]), int(best[1])]