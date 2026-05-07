def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)

    def xy(v):
        try:
            return (int(v[0]), int(v[1]))
        except:
            return (0, 0)

    sx, sy = xy(observation.get("self_position"))
    ox, oy = xy(observation.get("opponent_position"))

    obs = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = xy(p)
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = xy(r)
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

    midx = (w - 1) / 2.0
    # Strategy change vs pure "our side" bias: prioritize resources where we are clearly ahead,
    # otherwise pick the one that minimizes (my_dist - opp_dist) with a slight center preference.
    best = None
    best_score = None
    for (tx, ty) in resources:
        myd = cheb(sx, sy, tx, ty)
        opd = cheb(ox, oy, tx, ty)
        side_bonus = -0.10 * (abs(tx - midx))  # mild preference toward center for access to more
        ahead = myd - opd
        # Strongly favor being closer than opponent; deter targets opponent can snatch quickly.
        score = (ahead * 2.0) + myd * 0.15 + side_bonus
        if best_score is None or score < best_score:
            best_score = score
            best = (tx, ty)

    tx, ty = best
    dx = 0
    if tx > sx: dx = 1
    elif tx < sx: dx = -1
    dy = 0
    if ty > sy: dy = 1
    elif ty < sy: dy = -1

    nx, ny = sx + dx, sy + dy
    if (nx, ny) in obs:
        # Try alternate axis move if blocked.
        if dx != 0:
            alt = (sx, sy + dy)
            if alt not in obs and 0 <= alt[1] < h:
                return [0, dy]
        if dy != 0:
            alt = (sx + dx, sy)
            if alt not in obs and 0 <= alt[0] < w:
                return [dx, 0]
        return [0, 0]

    if not (0 <= nx < w and 0 <= ny < h):
        return [0, 0]
    return [dx, dy]