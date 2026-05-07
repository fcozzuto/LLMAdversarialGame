def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    best = None
    best_move = (0, 0)

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    for dxm, dym in moves:
        nx, ny = sx + dxm, sy + dym
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        # Find the target resource that gives maximal distance advantage to us
        best_adv = None
        best_our_d = None
        for rx, ry in resources:
            our_d = cheb(nx, ny, rx, ry)
            opp_d = cheb(ox, oy, rx, ry)
            adv = opp_d - our_d
            if (best_adv is None) or (adv > best_adv) or (adv == best_adv and our_d < best_our_d):
                best_adv = adv
                best_our_d = our_d

        # Tie-break: prefer closer to our best target; also prefer moves that reduce our nearest resource distance
        our_nearest = min(cheb(nx, ny, rx, ry) for rx, ry in resources)
        key = (best_adv, -our_nearest, -best_our_d, dxm, dym)
        if (best is None) or (key > best):
            best = key
            best_move = (dxm, dym)

    return [int(best_move[0]), int(best_move[1])]