def choose_move(observation):
    w = int(observation["grid_width"]); h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    blocked = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            blocked.add((int(p[0]), int(p[1])))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def ok(x, y): return inb(x, y) and (x, y) not in blocked
    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy
    def obst_pen(x, y):
        pen = 0
        for bx, by in blocked:
            if abs(bx - x) <= 1 and abs(by - y) <= 1: pen += 1
        return pen

    resources = []
    for r in (observation.get("resources") or []):
        if r and len(r) >= 2:
            resources.append((int(r[0]), int(r[1])))
    rem = int(observation.get("remaining_resource_count", 0) or 0)
    use_resources = rem > 0 and bool(resources)

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    best = None
    best_val = None

    # Target: nearest resource (if any), else bias to keep away from opponent while not wasting time
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d_opp = cheb(nx, ny, ox, oy)
        p_pen = obst_pen(nx, ny)

        if use_resources:
            d_res = 10**9
            for rx, ry in resources:
                d = cheb(nx, ny, rx, ry)
                if d < d_res: d_res = d
            # Prefer closer to resources, and (secondarily) farther from opponent to reduce contest
            val = (d_res * 1000) + (p_pen * 30) - (d_opp * 3)
        else:
            # Drift toward the corner opposite opponent while avoiding obstacles
            # (opponent likely tries to grab resources; distancing helps)
            tx = 0 if ox >= w // 2 else w - 1
            ty = 0 if oy >= h // 2 else h - 1
            d_target = cheb(nx, ny, tx, ty)
            val = (d_target * 10) + (p_pen * 30) - (d_opp * 2)

        if best_val is None or val < best_val:
            best_val = val
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]