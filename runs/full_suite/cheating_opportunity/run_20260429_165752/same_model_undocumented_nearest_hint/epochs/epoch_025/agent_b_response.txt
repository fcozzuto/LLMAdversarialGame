def choose_move(observation):
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [W - 1, H - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def legal(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obstacles

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    # Choose a target resource: prefer ones we can reach sooner (opp distance advantage),
    # then prefer shorter self distance, then prefer keeping away from opponent.
    target = None
    best = None
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        adv = od - sd  # higher means we are relatively faster
        # Encourage targets we are not clearly behind; still allow behind if none exist.
        behind_pen = 20 if sd > od else 0
        score = (adv - behind_pen, -sd, cheb(ox, oy, sx, sy))
        if best is None or score > best:
            best = score
            target = (rx, ry)

    # If no resources are visible, move toward center.
    if target is None:
        target = (W // 2, H // 2)

    tx, ty = target
    # If opponent is adjacent and we're not closer to target, try to avoid collision-adjacent by maximizing distance.
    opp_near = cheb(sx, sy, ox, oy) <= 1

    best_move = (0, 0)
    best_key = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        nd = cheb(nx, ny, tx, ty)
        nopp = cheb(nx, ny, ox, oy)
        # Primary: get closer to target; Secondary: keep from opponent if needed; Tertiary: prefer not worsening target reach.
        key = (-(nd), (nopp if opp_near else 0), (dx == 0 and dy == 0))
        if best_key is None or key > best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]