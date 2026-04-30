def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            try:
                obs.add((int(p[0]), int(p[1])))
            except:
                pass

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    resources = observation.get("resources") or []
    if resources:
        best = None
        best_r = None
        for r in resources:
            if not r or len(r) < 2:
                continue
            rx, ry = int(r[0]), int(r[1])
            if not valid(rx, ry):
                continue
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            adv = do - ds
            key = (adv, -ds, (rx * 9 + ry * 7) % 11)
            if best is None or key > best:
                best = key
                best_r = (rx, ry)
        rx, ry = best_r
        deltas = (-1, 0, 1)
        best_move = (0, 0)
        best_score = None
        for dx in deltas:
            for dy in deltas:
                nx, ny = sx + dx, sy + dy
                if not valid(nx, ny):
                    continue
                nds = cheb(nx, ny, rx, ry)
                ndo = cheb(ox, oy, rx, ry)
                # Prefer increasing advantage; then shorten own distance.
                score = (ndo - nds, -nds, -abs(nx - sx) - abs(ny - sy))
                if best_score is None or score > best_score:
                    best_score = score
                    best_move = (dx, dy)
        return [int(best_move[0]), int(best_move[1])]

    # No resources visible: drift toward center while staying safe.
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    deltas = (-1, 0, 1)
    best_move = (0, 0)
    best_score = None
    for dx in deltas:
        for dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            distc = cheb(nx, ny, int(round(cx)), int(round(cy)))
            # Deterministic tie-break by position.
            score = (-distc, -abs(nx - int(round(cx))) - abs(ny - int(round(cy))), (nx * 3 + ny * 5) % 13)
            if best_score is None or score > best_score:
                best_score = score
                best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]