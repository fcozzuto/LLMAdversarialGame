def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    role = str(observation.get("self_role") or "").lower()
    is_evader = "evader" in role

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            ax, ay = int(p[0]), int(p[1])
            if 0 <= ax < w and 0 <= ay < h:
                obs.add((ax, ay))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def cheb(ax, ay, bx, by):
        dx = abs(ax - bx); dy = abs(ay - by)
        return dx if dx > dy else dy

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    def best_corner_for_evader():
        # Evader prefers farthest corner from pursuer but also biased away from obstacles by preferring reachable neighbor cells.
        def corner_score(c):
            cx, cy = c
            base = cheb(ox, oy, cx, cy)
            # soft penalty if blocked at/near target
            pen = 0
            for nx, ny in ((cx, cy), (cx-1, cy), (cx+1, cy), (cx, cy-1), (cx, cy+1)):
                if (nx, ny) in obs:
                    pen += 1
            return base - 0.5 * pen
        return max(corners, key=corner_score)

    target_corner = best_corner_for_evader() if is_evader else min(corners, key=lambda c: cheb(ox, oy, c[0], c[1]))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    # Deterministic priority order for tie-break
    priority = {m: i for i, m in enumerate(moves)}

    best = None
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        # Core objective: chase (min distance) or evade (max distance)
        dist_to_opp = cheb(nx, ny, ox, oy)
        # Secondary objective: steer toward (pursuer blocks corners) / toward corner (evader)
        dist_to_target = cheb(nx, ny, target_corner[0], target_corner[1])
        # Heuristic: discourage "dead-end" moves with fewer options
        free = 0
        for ddx, ddy in moves:
            tx, ty = nx + ddx, ny + ddy
            if ok(tx, ty):
                free += 1
        # Also discourage staying adjacent if evader
        if dx == 0 and dy == 0:
            stay_pen = 1
        else:
            stay_pen = 0

        if is_evader:
            key = (-dist_to_opp, dist_to_target, -free, stay_pen, priority[(dx, dy)])
        else:
            key = (dist_to_opp, dist_to_target, -free, stay_pen, priority[(dx, dy)])

        if best_key is None or key < best_key:
            best_key = key
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]