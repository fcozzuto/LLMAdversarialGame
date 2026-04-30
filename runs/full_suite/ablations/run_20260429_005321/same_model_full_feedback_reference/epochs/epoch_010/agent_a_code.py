def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    obs = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = []
    for p in (observation.get("resources") or []):
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    me = (sx, sy)
    opp = (ox, oy)

    target = None
    if resources:
        best = -10**18
        for r in resources:
            myd = md(me, r)
            opd = md(opp, r)
            # Prefer resources we reach earlier; also prefer farther (larger myd) only if contest favors us.
            val = (opd - myd) * 5.0 - myd * 0.15 + (r[0] - r[1]) * 0.001
            if val > best:
                best = val
                target = r

    if target is None:
        # No resources: move to increase separation while staying safe.
        tx = w - 1 if ox < sx else 0
        ty = h - 1 if oy < sy else 0
        target = (tx, ty)

    tx, ty = target
    best_move = (0, 0)
    best_score = -10**18

    # Prefer greedy step towards target; fall back among safe moves minimizing distance to target.
    desired_dx = 0 if tx == sx else (1 if tx > sx else -1)
    desired_dy = 0 if ty == sy else (1 if ty > sy else -1)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        d_to_t = md((nx, ny), target)
        d_to_opp = md((nx, ny), opp)
        # Small preference for matching the greedy direction.
        dir_match = 1.0 if (dx == desired_dx and dy == desired_dy) else 0.0
        score = -d_to_t * 2.0 + d_to_opp * 0.05 + dir_match * 0.4 + (nx * 0.001 - ny * 0.0005)
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    dx, dy = best_move
    if not isinstance(dx, int):
        dx = int(dx)
    if not isinstance(dy, int):
        dy = int(dy)
    if dx < -1 or dx > 1 or dy < -1 or dy > 1:
        dx, dy = 0, 0
    return [dx, dy]