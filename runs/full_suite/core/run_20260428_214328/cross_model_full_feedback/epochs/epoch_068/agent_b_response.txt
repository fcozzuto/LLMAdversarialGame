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

    target = None
    best_score = None
    for rx, ry in resources:
        myd = dist_cheb((sx, sy), (rx, ry))
        od = dist_cheb((ox, oy), (rx, ry))
        score = (myd, -od)
        if best_score is None or score < best_score:
            best_score = score
            target = (rx, ry)

    if target is not None:
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
        # If moving would land on opponent, try to sidestep
        if (sx + dx, sy + dy) == (ox, oy):
            # try alternate axis
            if (sx + dx, sy) == (ox, oy) or not inside(sx + dx, sy):
                dx, dy = 0, (1 if ty > sy else -1) if ty != sy else (0)
            if (sx, sy + dy) == (ox, oy) or not inside(sx, sy + dy):
                dx, dy = (1 if tx > sx else -1) if tx != sx else 0, 0
    else:
        # No resource target: approach opponent defensively by staying or moving away gently
        dx = 0
        dy = 0
        if abs(ox - sx) >= abs(oy - sy):
            if ox > sx:
                dx = -1
            elif ox < sx:
                dx = 1
        else:
            if oy > sy:
                dy = -1
            elif oy < sy:
                dy = 1

    nx, ny = sx + dx, sy + dy
    if not inside(nx, ny) or (nx, ny) in obst:
        dx, dy = 0, 0
    return [dx, dy]