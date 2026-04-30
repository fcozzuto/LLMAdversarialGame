def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for b in observation.get("obstacles") or []:
        if b and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                blocked.add((bx, by))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if ok(rx, ry):
                resources.append((rx, ry))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(0, 0), (1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if ok(nx, ny):
            legal.append((dx, dy, nx, ny))

    if not legal:
        return [0, 0]

    if resources:
        best = None
        best_key = None
        for dx, dy, nx, ny in legal:
            # primary: maximize "resource advantage" = how much further opponent is than us
            top_adv = -10**9
            top_r = None
            top_ourd = 10**9
            for rx, ry in resources:
                ourd = cheb(nx, ny, rx, ry)
                oppd = cheb(ox, oy, rx, ry)
                adv = oppd - ourd
                if adv > top_adv or (adv == top_adv and ourd < top_ourd):
                    top_adv = adv
                    top_ourd = ourd
                    top_r = (rx, ry)
            # tie-breaks: keep opponent farther, and prefer smaller our distance to chosen resource
            rx, ry = top_r
            ourd = cheb(nx, ny, rx, ry)
            oppd = cheb(ox, oy, rx, ry)
            opp_far = oppd
            score_key = (top_adv, opp_far, -ourd, -abs((nx - rx)) - abs((ny - ry)), -(nx * 9 + ny), dx, dy)
            # deterministic: larger key is better; negate parts where needed above
            if best_key is None or score_key > best_key:
                best_key = score_key
                best = (dx, dy)
        return [int(best[0]), int(best[1])]

    # No visible resources: move to increase distance from opponent while staying safe
    best = None
    best_key = None
    for dx, dy, nx, ny in legal:
        d = cheb(nx, ny, ox, oy)
        # deterministic tie-break favor moving towards bottom-right-ish (fixed)
        key = (d, nx, ny)
        if best_key is None or key > best_key:
            best_key = key
            best = (dx, dy)
    return [int(best[0]), int(best[1])]