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
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    if not resources:
        best = (-10**9, 0, 0)
        for dxm, dym in moves:
            nx, ny = sx + dxm, sy + dym
            if not inb(nx, ny):
                continue
            score = cheb(nx, ny, int(cx), int(cy)) * -0.05 + cheb(nx, ny, ox, oy) * 0.01
            if score > best[0]:
                best = (score, dxm, dym)
        return [int(best[1]), int(best[2])]

    best_score = -10**18
    best_move = (0, 0)

    for dxm, dym in moves:
        nx, ny = sx + dxm, sy + dym
        if not inb(nx, ny):
            continue

        our_nearest = 10**9
        best_margin = -10**9
        for rx, ry in resources:
            ourd = cheb(nx, ny, rx, ry)
            oppd = cheb(ox, oy, rx, ry)
            if ourd < our_nearest:
                our_nearest = ourd
            margin = oppd - ourd
            if margin > best_margin:
                best_margin = margin

        # Favor moves that can reach some resource no later than opponent (positive margin),
        # and otherwise minimize our nearest resource distance.
        center_tie = -cheb(nx, ny, int(cx), int(cy)) * 0.001
        safety = cheb(nx, ny, ox, oy) * 0.002  # slight move-away from opponent
        if best_margin >= 0:
            score = best_margin * 2.0 - our_nearest * 0.15 + center_tie + safety
        else:
            score = -our_nearest * 1.0 + best_margin * 0.3 + center_tie + safety

        if score > best_score:
            best_score = score
            best_move = (dxm, dym)

    return [int(best_move[0]), int(best_move[1])]