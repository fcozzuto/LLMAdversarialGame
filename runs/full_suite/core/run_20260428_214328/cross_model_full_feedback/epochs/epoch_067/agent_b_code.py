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

    def dist_cheb(a, b):
        return max(abs(a[0]-b[0]), abs(a[1]-b[1]))

    # Prefer going toward closest resource while keeping distance from opponent
    best = None
    best_score = None
    for rx, ry in resources:
        myd = dist_cheb((sx, sy), (rx, ry))
        od = dist_cheb((ox, oy), (rx, ry))
        score = (myd, -od)
        if best_score is None or score < best_score:
            best_score = score
            best = (rx, ry)

    if best is not None:
        tx, ty = best
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
        # Validate move
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obst:
            return [0, 0]
        return [dx, dy]

    # If no resource targets, move to maintain safe distance from opponent
    dx = 0
    dy = 0
    if ox > sx:
        dx = -1
    elif ox < sx:
        dx = 1
    if oy > sy:
        dy = -1
    elif oy < sy:
        dy = 1
    nx, ny = sx + dx, sy + dy
    if not inside(nx, ny) or (nx, ny) in obst:
        return [0, 0]
    return [dx, dy]