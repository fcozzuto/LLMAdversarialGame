def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def dist_cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        # Fallback: move toward opponent to contest space a bit
        best_move = (0, 0)
        best_sc = -10**18
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            sc = -dist_cheb(nx, ny, ox, oy)
            if sc > best_sc:
                best_sc = sc
                best_move = (dx, dy)
        return [best_move[0], best_move[1]]

    # Pick target resource where we have the most advantage (opp_dist - my_dist)
    my_d_to = None
    target = resources[0]
    best_adv = -10**18
    best_my = 10**9
    for rx, ry in resources:
        myd = dist_cheb(sx, sy, rx, ry)
        opd = dist_cheb(ox, oy, rx, ry)
        adv = opd - myd
        if adv > best_adv or (adv == best_adv and (myd < best_my or (myd == best_my and (rx, ry) < target))):
            best_adv = adv
            best_my = myd
            target = (rx, ry)

    tx, ty = target

    # Choose move to reduce distance to target; small tie-break to stay away from opponent when possible
    best_move = (0, 0)
    best_sc = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        nd = dist_cheb(nx, ny, tx, ty)
        od = dist_cheb(nx, ny, ox, oy)
        # Prefer getting closer; if we're similarly close, prefer being farther from opponent (less likely to be stolen)
        sc = -nd * 10 + od * 0.1
        if sc > best_sc or (sc == best_sc and (dx, dy) < best_move):
            best_sc = sc
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]