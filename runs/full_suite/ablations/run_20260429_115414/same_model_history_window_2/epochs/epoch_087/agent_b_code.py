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

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in blocked:
                resources.append((rx, ry))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    candidates = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if legal(nx, ny):
            candidates.append((nx, ny, dx, dy))

    if not candidates:
        return [0, 0]

    best = None
    # Main idea: for each candidate, pick the resource where we have the biggest distance advantage.
    for nx, ny, dx, dy in candidates:
        if resources:
            best_adv = None
            for rx, ry in resources:
                ds = cheb(nx, ny, rx, ry)
                do = cheb(ox, oy, rx, ry)
                adv = do - ds  # positive if we are closer than opponent
                if best_adv is None or adv > best_adv[0] or (adv == best_adv[0] and ds < best_adv[1]):
                    best_adv = (adv, ds)
            adv, ds = best_adv
            # Encourage large advantage and then closer pick-up; also softly avoid being near opponent (reduce swap opportunities).
            score = adv * 10 - ds - 0.05 * cheb(nx, ny, ox, oy)
        else:
            # No resources visible: drift to center while not suicidally approaching opponent.
            cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
            dc = cheb(nx, ny, cx, cy)
            score = -dc - 0.02 * cheb(nx, ny, ox, oy)
        if best is None or score > best[0]:
            best = (score, dx, dy)

    return [int(best[1]), int(best[2])]