def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    resources = []
    for r in (observation.get("resources") or []):
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if inb(x, y):
                resources.append((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best_move = [0, 0]
        best_val = -10**9
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            # Prefer moving toward center while slightly away from opponent
            val = -cheb(nx, ny, cx, cy) + 0.1 * cheb(nx, ny, ox, oy)
            if val > best_val:
                best_val, best_move = val, [dx, dy]
        return best_move

    best_r = resources[0]
    best_adv = -10**18
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        adv = (od - sd) - 0.05 * sd  # steal/contesting preference; deterministic bias to closer when equal
        if adv > best_adv:
            best_adv, best_r = adv, (rx, ry)

    tx, ty = best_r
    best_move = [0, 0]
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        nd = cheb(nx, ny, tx, ty)
        # immediate advantage proxy: how much closer we are than opponent is to target
        od = cheb(ox, oy, tx, ty)
        score = (od - nd) * 100 - nd  # prioritize reducing our distance, but only to target where we can contest
        if score > best_score:
            best_score, best_move = score, [dx, dy]
    return best_move