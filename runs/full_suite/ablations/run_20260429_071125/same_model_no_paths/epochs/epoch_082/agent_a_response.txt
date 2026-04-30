def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    # Pick a materially different deterministic target policy:
    # If opponent is already significantly closer (within 1 step advantage), deny their best by contesting it.
    # Otherwise, race to the best resource based on relative advantage and distance.
    best_deny = None
    best_deny_key = None
    best_race = None
    best_race_key = None
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        # deny key: favor resources where opponent is closer by at least 1
        deny_key = (opd - myd, myd, -rx, -ry)  # smaller first element means opponent closer
        if best_deny_key is None or deny_key < best_deny_key:
            best_deny_key = deny_key
            best_deny = (rx, ry)
        # race key: favor higher relative advantage and closer target
        race_key = (-(opd - myd), -myd, rx, ry)  # prefer I am closer; tie by shorter distance
        if best_race_key is None or race_key > best_race_key:
            best_race_key = race_key
            best_race = (rx, ry)

    tx, ty = best_deny
    myd_deny = cheb(sx, sy, tx, ty)
    opd_deny = cheb(ox, oy, tx, ty)
    if not (opd_deny - myd_deny >= 1):  # if not clearly opponent-advantaged, go race instead
        tx, ty = best_race
    # Greedy step with obstacle avoidance, breaking ties deterministically
    def ok(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in blocked

    best_step = (0, 0)
    best_step_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d_to = cheb(nx, ny, tx, ty)
        # secondary: reduce opponent closeness to the same target (denial effect)
        opp_d = cheb(ox, oy, tx, ty)
        # if stepping onto a resource tile is possible, prioritize it
        on_res = 1 if (nx, ny) == (tx, ty) else 0
        key = (-on_res, d_to, (opp_d - cheb(nx, ny, tx, ty)), dx, dy)
        if best_step_key is None or key < best_step_key:
            best_step_key = key
            best_step = (dx, dy)

    return [int(best_step[0]), int(best_step[1])]