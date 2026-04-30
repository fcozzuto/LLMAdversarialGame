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

    def dist_cheb(a, b):
        return max(abs(a[0]-b[0]), abs(a[1]-b[1]))

    target = None
    best_score = None
    for rx, ry in resources:
        myd = dist_cheb((sx, sy), (rx, ry))
        od = dist_cheb((ox, oy), (rx, ry))
        score = (myd, -od)
        if best_score is None or score < best_score:
            best_score = score
            target = (rx, ry)

    if target is None:
        return [0, 0]

    tx, ty = target
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

    cand = [dx, dy]
    # Ensure move stays within bounds; otherwise stay
    nx, ny = sx + cand[0], sy + cand[1]
    if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obst:
        return [0, 0]
    return cand