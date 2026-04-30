def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    me = observation.get("self_position", [0, 0]) or [0, 0]
    opp = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(me[0]), int(me[1])
    ox, oy = int(opp[0]), int(opp[1])

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

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def score_pos(x, y):
        if (x, y) == (ox, oy):
            return -10**9
        if resources:
            best = -10**9
            for rx, ry in resources:
                d_me = cheb(x, y, rx, ry)
                d_opp = cheb(ox, oy, rx, ry)
                # If I'm already ahead on this resource, prioritize fastest; else prioritize blocking
                if d_me <= d_opp:
                    v = 2000 - 50 * d_me
                else:
                    v = 800 - 60 * (d_me - d_opp)  # reduce opponent advantage by closing gap
                # Prefer positions that keep distance from opponent unless blocking
                v -= 8 * cheb(x, y, ox, oy)
                # Mild preference for approaching center to avoid dead-ends
                v -= 0.5 * (abs((w - 1) / 2.0 - rx) + abs((h - 1) / 2.0 - ry)) * 0.0
                if v > best:
                    best = v
            return best
        # No visible resources: move to maximize distance while still drifting toward center
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        return -10 * cheb(x, y, ox, oy) - (abs(x - cx) + abs(y - cy))

    # If paths are gone, change tactic: sometimes head directly to closest resource to avoid stalling
    ti = int(observation.get("turn_index", 0) or 0)
    prefer_direct = (ti % 2 == 0)

    best_move = (0, 0)
    best_val = -10**18

    # Deterministic tie-break: fixed move order already
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        v = score_pos(nx, ny)
        if prefer_direct and resources:
            # Directly chase nearest resource as a secondary boost
            nd = 10**9
            for rx, ry in resources:
                d = cheb(nx, ny, rx, ry)
                if d < nd:
                    nd = d
            v += 40 - 6 * nd
        if v > best_val:
            best_val = v
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]