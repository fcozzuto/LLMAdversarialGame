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

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if resources:
        best = None
        best_score = None
        for rx, ry in resources:
            myd = cheb(sx, sy, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            # Prefer resources where we are closer; if tied, prefer earlier-ish (smaller both distances).
            score = (opd - myd, -(myd + opd), -(rx + 3 * ry))
            if best is None or score > best_score:
                best_score, best = score, (rx, ry)
        tx, ty = best
    else:
        # No visible resources: move toward opponent's side (center-biased) to regain tempo.
        target_list = []
        for cx in (w // 2,):
            for cy in (h // 2,):
                target_list.append((cx, cy))
        # If opponent is far, drift toward it; otherwise toward center.
        tx, ty = (ox, oy) if cheb(sx, sy, ox, oy) > cheb(sx, sy, w // 2, h // 2) else target_list[0]

    # Choose one step that minimizes distance to target, with a secondary aim to reduce opponent's advantage.
    best_move = (0, 0)
    best_key = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        myd2 = cheb(nx, ny, tx, ty)
        opd2 = cheb(ox, oy, tx, ty)
        # If opponent could be closer after we move, penalize; otherwise reward progress.
        key = (myd2, (opd2 - myd2), dx == 0 and dy == 0, abs(nx - tx) + abs(ny - ty))
        if best_key is None or key < best_key:
            best_key, best_move = key, (dx, dy)

    return [int(best_move[0]), int(best_move[1])]