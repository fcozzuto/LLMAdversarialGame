def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)

    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
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

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources:
        # Defensive: drift away from opponent a bit, otherwise stay.
        best = (0, 0)
        best_sc = -10**18
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            d_op = cheb(nx, ny, ox, oy)
            sc = d_op
            if sc > best_sc or (sc == best_sc and (dx, dy) < best):
                best_sc = sc
                best = (dx, dy)
        return [best[0], best[1]]

    # Target selection: maximize advantage (opponent slow relative to self), then prefer nearer-to-self.
    best_r = None
    best_sc = -10**18
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        # Hard-favor resources where we arrive earlier; otherwise choose the least-bad.
        sc = (od - sd) * 1000 - sd
        if sc > best_sc:
            best_sc = sc
            best_r = (rx, ry)

    rx, ry = best_r

    # Greedy move toward target that preserves the advantage; deterministic tie-break.
    best_move = (0, 0)
    best_score = -10**18
    # Tie-break preference order to keep deterministic: smaller dx, then smaller dy.
    # We'll incorporate it into score slightly.
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        nsd = cheb(nx, ny, rx, ry)
        nod = cheb(ox, oy, rx, ry)
        adv = nod - nsd
        sc = adv * 1000 - nsd
        sc -= abs(dx) * 3 + abs(dy)  # slight preference for straighter/less moving
        sc -= (dx + 1) * 0.001 + (dy + 1) * 0.0001
        if sc > best_score:
            best_score = sc
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]