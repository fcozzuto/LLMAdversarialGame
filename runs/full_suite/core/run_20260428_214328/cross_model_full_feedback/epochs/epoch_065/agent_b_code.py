def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    obst = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inside(x, y):
                obst.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inside(x, y) and (x, y) not in obst:
                resources.append((x, y))

    # Simple deterministic heuristic:
    # 1) If a resource exists, move toward the closest one (Chebyshev),
    #    breaking ties by being farther from opponent.
    # 2) Otherwise, move toward center while avoiding obstacles and staying within bounds.
    def dist_cheb(a, b):
        return max(abs(a[0]-b[0]), abs(a[1]-b[1]))

    target = None
    if resources:
        best = None
        best_score = None
        for rx, ry in resources:
            d = dist_cheb((sx, sy), (rx, ry))
            od = dist_cheb((ox, oy), (rx, ry))
            score = (d, od)
            if best_score is None or score < best_score:
                best = (rx, ry)
                best_score = score
        target = best

    moves = []
    if target is not None:
        dx = target[0] - sx
        dy = target[1] - sy
        # clamp to -1,0,1
        ix = -1 if dx < 0 else (1 if dx > 0 else 0)
        iy = -1 if dy < 0 else (1 if dy > 0 else 0)
        nx, ny = sx + ix, sy + iy
        if inside(nx, ny) and (nx, ny) not in obst:
            return [ix, iy]

    # No resource or blocked path: move towards center while avoiding obstacles
    cx, cy = w // 2, h // 2
    dx = cx - sx
    dy = cy - sy
    ix = -1 if dx < 0 else (1 if dx > 0 else 0)
    iy = -1 if dy < 0 else (1 if dy > 0 else 0)
    # Try primary toward center; if blocked, try alternatives
    candidates = []
    for ax in (-1, 0, 1):
        for ay in (-1, 0, 1):
            if ax == 0 and ay == 0:
                continue
            nx, ny = sx + ax, sy + ay
            if not inside(nx, ny):
                continue
            if (nx, ny) in obst:
                continue
            score = (abs(cx - nx) + abs(cy - ny), abs(ox - nx) + abs(oy - ny))
            candidates.append(((ax, ay), score))
    if candidates:
        candidates.sort(key=lambda t: t[1])
        return [candidates[0][0][0], candidates[0][0][1]]

    # If no move possible, stay
    return [0, 0]