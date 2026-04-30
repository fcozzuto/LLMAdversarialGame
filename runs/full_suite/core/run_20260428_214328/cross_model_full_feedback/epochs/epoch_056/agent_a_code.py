def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (w - 1, h - 1)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    obstacles = observation.get("obstacles") or []
    resources = observation.get("resources") or []

    def inside(x, y): return 0 <= x < w and 0 <= y < h
    def cheb(ax, ay, bx, by):
        dx = ax - bx; dx = -dx if dx < 0 else dx
        dy = ay - by; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy

    obst = set()
    for p in obstacles:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inside(x, y): obst.add((x, y))

    res = []
    for p in resources:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inside(x, y) and (x, y) not in obst:
                res.append((x, y))
    if not res:
        tx, ty = w // 2, h // 2
        dx = tx - sx; dx = -1 if dx < 0 else (1 if dx > 0 else 0)
        dy = ty - sy; dy = -1 if dy < 0 else (1 if dy > 0 else 0)
        return [dx, dy]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = (0, 0)
    best_val = -10**18

    # Prefer moves that maximize (opp_dist - self_dist) to some resource; tie-break by closer to center and safer from obstacles.
    center = (w // 2, h // 2)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obst:
            continue
        step_val = 0
        # Evaluate top few resources only for speed/determinism.
        # Choose deterministically by best resource advantage; also account for ability to reach with smaller distance.
        best_adv_for_move = -10**18
        for (rx, ry) in res[:]:
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            adv = od - sd  # positive means we are closer than opponent to that resource
            val = adv * 100 - sd
            if rx == center[0] and ry == center[1]:
                val += 3
            if val > best_adv_for_move:
                best_adv_for_move = val
        step_val = best_adv_for_move
        # Small preference for staying away from obstacles (count blocked neighbors)
        block_pen = 0
        for ddx, ddy in moves:
            ax, ay = nx + ddx, ny + ddy
            if not inside(ax, ay) or (ax, ay) in obst:
                block_pen += 1
        step_val -= block_pen * 0.05
        # If equal, prefer increasing distance from opponent (reduce their ability to contest)
        if step_val > best_val:
            best_val = step_val
            best = (dx, dy)
        elif step_val == best_val:
            if cheb(nx, ny, ox, oy) > cheb(sx, sy, ox, oy):
                best = (dx, dy)

    return [int(best[0]), int(best[1])]