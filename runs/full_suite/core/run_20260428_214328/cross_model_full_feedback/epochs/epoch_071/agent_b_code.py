def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obst = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                resources.append((x, y))

    # Simple deterministic heuristic: move towards closest resource while staying away from opponent
    if not resources:
        # If no resources, try to reposition toward center while avoiding obstacles
        dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
        best = None
        best_score = -10**9
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obst:
                dist_op = abs(nx - ox) + abs(ny - oy)
                dist_center = abs(nx - w//2) + abs(ny - h//2)
                score = -dist_center - dist_op
                if score > best_score:
                    best_score = score
                    best = (dx, dy)
        if best is None:
            return [0, 0]
        return [best[0], best[1]]

    # Find nearest resource by Chebyshev distance
    def dist_cheb(a, b):
        return max(abs(a[0]-b[0]), abs(a[1]-b[1]))
    best_target = None
    best_score = None
    for rx, ry in resources:
        myd = dist_cheb((sx, sy), (rx, ry))
        od = dist_cheb((ox, oy), (rx, ry))
        score = (myd, -od)
        if best_score is None or score < best_score:
            best_score = score
            best_target = (rx, ry)
    if best_target is None:
        return [0, 0]

    tx, ty = best_target
    dx = 0
    if tx > sx:
        dx = 1
    elif tx < sx:
        dx = -1
    dy = 0
    if ty > sy:
        dy = 1
    elif ty < sy:
        dy = -1

    nx, ny = sx + dx, sy + dy
    if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obst:
        return [dx, dy]
    # If blocked, try alternative deterministic moves towards target or stay
    for adx in (-1, 0, 1):
        for ady in (-1, 0, 1):
            if adx == 0 and ady == 0:
                continue
            tx2, ty2 = sx + adx, sy + ady
            if 0 <= tx2 < w and 0 <= ty2 < h and (tx2, ty2) not in obst:
                return [adx, ady]
    return [0, 0]