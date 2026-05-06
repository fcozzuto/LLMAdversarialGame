def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def clamp_step(a, b):
        d = b - a
        return 0 if d == 0 else (1 if d > 0 else -1)

    remaining = int(observation.get("remaining_resource_count", len(resources)))
    my_near = None
    my_near_adv = None

    for rx, ry in resources:
        md = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        adv = md - od  # negative => I am closer
        if my_near is None or (adv, md, rx, ry) < (my_near_adv, 10**9, 10**9, 10**9):
            my_near = (rx, ry)
            my_near_adv = adv

    # Strategic switch:
    # If opponent threatens the nearest resource, actively grab a resource where I are comparatively ahead.
    # Otherwise, keep pressure by going to the nearest resource.
    if remaining <= 6 or my_near_adv is not None and my_near_adv <= 0:
        target = min(resources, key=lambda r: (cheb(sx, sy, r[0], r[1]), cheb(ox, oy, r[0], r[1]), r[0], r[1]))
    else:
        # Pick resource maximizing (opponent distance - my distance) (i.e., I can arrive earlier),
        # tie-break by smallest my distance to keep momentum.
        target = min(resources, key=lambda r: (- (cheb(ox, oy, r[0], r[1]) - cheb(sx, sy, r[0], r[1])), cheb(sx, sy, r[0], r[1]), r[0], r[1]))

    tx, ty = target
    dx = clamp_step(sx, tx)
    dy = clamp_step(sy, ty)

    nx, ny = sx + dx, sy + dy
    if (nx, ny) in obs or not (0 <= nx < w and 0 <= ny < h):
        # fallback: try any valid step that reduces cheb distance to target
        moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
        best = None
        for mx, my in moves:
            px, py = sx + mx, sy + my
            if 0 <= px < w and 0 <= py < h and (px, py) not in obs:
                score = (cheb(px, py, tx, ty), cheb(px, py, ox, oy), px, py)
                if best is None or score < best[0]:
                    best = (score, mx, my)
        return [best[1], best[2]] if best is not None else [0, 0]

    return [dx, dy]