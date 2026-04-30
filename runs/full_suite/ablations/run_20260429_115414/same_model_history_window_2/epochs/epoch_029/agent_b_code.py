def choose_move(observation):
    w = int(observation["grid_width"]); h = int(observation["grid_height"])
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles") or []
    resources = observation.get("resources") or []
    blocked = set()
    for p in obstacles:
        if p and len(p) >= 2:
            blocked.add((int(p[0]), int(p[1])))

    res = []
    for r in resources:
        if r and len(r) >= 2:
            res.append((int(r[0]), int(r[1])))
    rem = int(observation.get("remaining_resource_count", 0) or 0)

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def ok(x, y): return inb(x, y) and (x, y) not in blocked
    def cheb(ax, ay, bx, by):
        dx = ax - bx; dx = -dx if dx < 0 else dx
        dy = ay - by; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    # Strategy:
    # - If resources remain: greedily go to the "most urgent" resource (min distance), with tie-break by opponent distance.
    # - If no resources remain: keep far from opponent and avoid blocked squares around them.
    target = None
    if rem > 0 and res:
        # urgency: prioritize reachable-near target; tie-break by keeping away from opponent (so we don't contest)
        best = None; best_key = None
        for rx, ry in res:
            d = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            key = (d, -do, rx, ry)
            if best_key is None or key < best_key:
                best_key = key; best = (rx, ry)
        target = best

    def opp_pressure(x, y):
        # discourage stepping close to opponent, but allow if it advances to target
        return cheb(x, y, ox, oy)

    def near_block_pen(x, y):
        pen = 0
        for bx, by in blocked:
            if abs(bx - x) <= 1 and abs(by - y) <= 1:
                pen += 1
        return pen

    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        if target is not None:
            dcur = cheb(sx, sy, target[0], target[1])
            dnew = cheb(nx, ny, target[0], target[1])
            # primary: reduce distance to target; secondary: keep away from opponent; tertiary: avoid block vicinity
            val = (dnew, opp_pressure(nx, ny), near_block_pen(nx, ny), dx, dy)
            # choose minimal lexicographic
            if best_val is None or val < best_val:
                best_val = val; best_move = (dx, dy)
        else:
            # no resources: maximize distance from opponent (minimize cheb), but avoid moving into block-adjacent squares
            val = (-opp_pressure(nx, ny), near_block_pen(nx, ny), dx, dy)
            # choose lexicographic minimal by negative pressure and penalties
            if best_val is None or val < best_val:
                best_val = val; best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]