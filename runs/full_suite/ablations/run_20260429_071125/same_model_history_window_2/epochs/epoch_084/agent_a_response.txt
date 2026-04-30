def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obst = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    candidates = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def best_target(px, py):
        best = None
        best_adv = -10**18
        for rx, ry in resources:
            d_self = cheb(px, py, rx, ry)
            d_opp = cheb(ox, oy, rx, ry)
            adv = d_opp - d_self
            if adv > best_adv or (adv == best_adv and (best is None or (rx, ry) < best)):
                best_adv = adv
                best = (rx, ry)
        return best, best_adv

    # Try to maximize advantage on the next step; add a small tie-break for reducing our distance.
    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obst:
            continue

        tgt, adv = best_target(nx, ny)
        if tgt is None:
            continue
        rx, ry = tgt
        d_self = cheb(nx, ny, rx, ry)
        # Also slightly prefer moves that keep opponent farther from our best target (more blocking).
        d_opp = cheb(ox, oy, rx, ry)

        # Small secondary preference: be closer to center when advantage is tied.
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        center_pen = abs(nx - cx) + abs(ny - cy)

        score = adv * 1000 + (d_opp - d_self) * 50 - d_self * 2 - center_pen * 0.01
        if score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]