def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    obst = set()
    for p in (observation.get("obstacles", []) or []):
        try:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obst.add((x, y))
        except:
            pass

    resources = []
    for r in (observation.get("resources", []) or []):
        try:
            x, y = int(r[0]), int(r[1])
            if inb(x, y) and (x, y) not in obst:
                resources.append((x, y))
        except:
            pass

    if not resources:
        return [0, 0]

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    legal = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obst:
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Pick a contest target: maximize advantage (opp_dist - self_dist)
    best_res = None
    best_adv = -10**9
    for (rx, ry) in resources:
        a = cheb(ox, oy, rx, ry) - cheb(sx, sy, rx, ry)
        if a > best_adv:
            best_adv = a
            best_res = (rx, ry)

    rx, ry = best_res
    # If we are not advantaged for any resource, fall back to nearest resource.
    if best_adv <= 0:
        d0 = 10**9
        for (r2x, r2y) in resources:
            d = cheb(sx, sy, r2x, r2y)
            if d < d0:
                d0 = d
                rx, ry = r2x, r2y

    # Choose move that improves our distance to target; tie-break by improving our "min advantage".
    best_move = (0, 0)
    best_val = -10**9
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        d_self = cheb(nx, ny, rx, ry)
        # Negative distance is better.
        val = -d_self * 10
        # Tie-break: how close we get to any resource relative to opponent.
        min_gap = 10**9
        for (r2x, r2y) in resources:
            gap = cheb(ox, oy, r2x, r2y) - cheb(nx, ny, r2x, r2y)
            if gap < min_gap:
                min_gap = gap
        val += min_gap
        # Deterministic tie-break: lexicographic by move preference order already stable.
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]