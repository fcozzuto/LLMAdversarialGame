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

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if ok(rx, ry):
                resources.append((rx, ry))

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    cx, cy = w // 2, h // 2

    best = None
    best_sc = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            sc = -10**15
        else:
            # Prefer moves that get closer than opponent to some resource (strong), then prefer center.
            if resources:
                max_adv = -10**18
                min_self = 10**18
                min_center = 10**18
                for rx, ry in resources:
                    sd = cheb(nx, ny, rx, ry)
                    od = cheb(ox, oy, rx, ry)
                    adv = od - sd
                    if adv > max_adv: max_adv = adv
                    if sd < min_self: min_self = sd
                    dc = abs(rx - cx) + abs(ry - cy)
                    if dc < min_center: min_center = dc
                # Mild repulsion from opponent to reduce accidental tradeoffs.
                opp_pen = 0
                dpo = cheb(nx, ny, ox, oy)
                if dpo == 0:
                    opp_pen = 500
                sc = max_adv * 80 - min_self * 3 - min_center * 0.5 - opp_pen
            else:
                d_to_center = abs(nx - cx) + abs(ny - cy)
                dpo = cheb(nx, ny, ox, oy)
                sc = -d_to_center * 2 + dpo * 0.25
        # Deterministic tie-break: fixed move order.
        if sc > best_sc:
            best_sc = sc
            best = [dx, dy]
    return best