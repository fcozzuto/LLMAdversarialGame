def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocked = set()
    for p in observation.get("obstacles", []) or []:
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))
        except:
            pass

    resources = []
    for r in observation.get("resources", []) or []:
        try:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                resources.append((x, y))
        except:
            pass
    if not resources:
        return [0, 0]

    def cheb(a, b):
        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])
        return dx if dx > dy else dy

    def manh(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    my = (sx, sy)
    opp = (ox, oy)

    # Target choice: prioritize resources where we are closer than opponent,
    # but heavily penalize resources likely to be "on their sweep line" (same y).
    best = None
    best_key = None
    for r in resources:
        myd = cheb(my, r)
        opd = cheb(opp, r)
        sweep_pen = 6 if r[1] == oy else 0
        # smaller key is better
        key = ((myd - opd) + sweep_pen, myd, -r[0], r[1])
        if best_key is None or key < best_key:
            best_key = key
            best = r
    tx, ty = best

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cand = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in blocked:
            continue
        my2 = (nx, ny)
        d_my = cheb(my2, (tx, ty))
        d_opp = cheb(opp, (tx, ty))
        # If opponent isn't getting any closer to the same target, prefer faster approach.
        # If opponent is close, try to keep them farther from it while we advance.
        key = (d_my, d_opp - d_my, manh(my2, (tx, ty)), -d_opp)
        cand.append((key, dx, dy))
    if not cand:
        return [0, 0]

    cand.sort(key=lambda t: t[0])
    return [int(cand[0][1]), int(cand[0][2])]