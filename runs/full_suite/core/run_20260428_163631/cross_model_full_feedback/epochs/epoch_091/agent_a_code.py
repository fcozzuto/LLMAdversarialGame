def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if inb(x, y) and (x, y) not in obstacles:
                resources.append((x, y))

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    legal = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    opp = (ox, oy)
    me = (sx, sy)

    d_opp = dist(me, opp)
    target = None
    if resources:
        bestd = 10**9
        for rr in resources:
            dd = dist(me, rr)
            if dd < bestd:
                bestd = dd
                target = rr

    # Score each legal move; tie-break by fixed move order (deltas iteration).
    best_move = legal[0]
    best_val = -10**18
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        nm = (nx, ny)
        val = 0
        if target is not None:
            val += 1000 - 3 * dist(nm, target)
        # Avoid getting too close to opponent
        val += 20 * (d_opp if d_opp > 2 else -dist(nm, opp))
        if d_opp <= 2:
            val += 200 * dist(nm, opp)
        # Prefer staying on board (already ensured) and slightly reduce aimless moves
        if (dx, dy) == (0, 0):
            val -= 1
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]