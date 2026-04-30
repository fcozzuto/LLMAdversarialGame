def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obst = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = []
    seen = set()
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst and (x, y) not in seen:
                resources.append((x, y))
                seen.add((x, y))

    def cheb(a, b):
        return abs(a[0] - b[0]) if abs(a[0] - b[0]) >= abs(a[1] - b[1]) else abs(a[1] - b[1])

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    me = (sx, sy)
    opp = (ox, oy)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    # Choose target with best "advantage"; if none, grab closest resource.
    target = None
    best_adv = -10**9
    if resources:
        for r in resources:
            da = cheb(me, r)
            db = cheb(opp, r)
            adv = db - da  # positive means we're closer
            if adv > best_adv:
                best_adv = adv
                target = r
        if best_adv < 0:
            target = min(resources, key=lambda r: cheb(me, r))

    # If no resources visible, hold line near center-ish and avoid walls/obstacles.
    if target is None:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        target = (min(max(cx, 0), w - 1), min(max(cy, 0), h - 1))

    tx, ty = target
    best_move = (0, 0)
    best_val = -10**18

    # Deterministic tie-break order via fixed moves list.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obst:
            continue

        our_d = cheb((nx, ny), (tx, ty))
        opp_d = cheb(opp, (tx, ty))

        # Prefer moves that reduce our distance; contest by also considering whether we delay opponent.
        # Also mildly avoid approaching opponent too directly unless contesting.
        sep = cheb((nx, ny), opp)
        opp_sep = cheb(me, opp)

        contest = 1.0 if (opp_d <= our_d + 1) else 0.3
        val = (-our_d * 10.0) + ((opp_d - our_d) * 6.0 * contest) + ((sep - opp_sep) * 1.5)
        # Obstacle-adjacent moves are slightly discouraged to reduce accidental dead-ends.
        adj_obst = 0
        for adx, ady in [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(1,1),(-1,1),(1,-1)]:
            ax, ay = nx + adx, ny + ady
            if 0 <= ax < w and 0 <= ay < h and (ax, ay) in obst:
                adj_obst += 1
        val -= adj_obst * 0.8

        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]