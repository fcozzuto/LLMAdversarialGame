def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def md(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    # Fallback target: push toward opponent's side deterministically
    if resources:
        far_corner = (w - 1, h - 1)
    else:
        far_corner = (w - 1 if sx < ox else 0, h - 1 if sy < oy else 0)

    opp_term = 0
    if resources:
        # when we can't lead any resource, prioritize escaping
        mind_opp = 10**9
        for rx, ry in resources:
            d = md(ox, oy, rx, ry)
            if d < mind_opp:
                mind_opp = d
        opp_term = mind_opp

    best = (0, 0)
    bestv = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        score = 0
        if not resources:
            tx, ty = far_corner
            myd = md(nx, ny, tx, ty)
            # Prefer moving away from opponent while advancing to corner
            myopp = md(nx, ny, ox, oy)
            score = (-myd * 2) + (myopp * 1)
        else:
            myopp_now = md(nx, ny, ox, oy)
            for rx, ry in resources:
                myd = md(nx, ny, rx, ry)
                od = md(ox, oy, rx, ry)
                lead = od - myd  # positive means we are closer or arrive sooner in steps
                # Capture/lead first, then distance; de-emphasize resources we are unlikely to reach
                if lead > 0:
                    score += 60 * lead - 3 * myd
                else:
                    score += 10 * lead - 1.5 * myd
            # If we're not leading much, avoid going into opponent pressure
            # (deterministic: based on closeness to opponent)
            score += (myopp_now - opp_term) * 0.5

        # Small tie-breaker: prefer staying deterministic toward increasing x then y
        if score > bestv + 1e-9 or (abs(score - bestv) <= 1e-9 and (dx, dy) > best):
            bestv = score
            best = (dx, dy)

    return [int(best[0]), int(best[1])]