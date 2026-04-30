def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        best = None
        bestv = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny) and not (nx == sx and ny == sy):
                continue
            v = man(nx, ny, ox, oy)
            if v > bestv or (v == bestv and (nx + ny) % 2 == 0):
                bestv = v
                best = (dx, dy)
        return [int(best[0]), int(best[1])]

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    best_move = (0, 0)
    best_score = -10**18

    # Choose targets with preference: closer to us, farther from opponent.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) and not (nx == sx and ny == sy):
            continue

        # Predict best attainable resource from next position.
        local_best = -10**18
        for rx, ry in resources:
            dself = man(nx, ny, rx, ry)
            dopp = man(ox, oy, rx, ry)
            # Higher is better: minimize our distance, maximize opponent distance.
            # Add slight center preference to avoid circling.
            center_bias = -0.02 * (abs(nx - cx) + abs(ny - cy))
            score = (-1.2 * dself) + (0.65 * dopp) + center_bias
            # Small tie-break towards lower coords deterministically
            score += -0.0001 * (rx * 11 + ry * 7)
            if score > local_best:
                local_best = score

        # Extra safety: if opponent is adjacent and we can avoid it, prefer not to move closer.
        opp_adj = man(nx, ny, ox, oy)
        opp_pen = 0.0
        if opp_adj <= 1:
            opp_pen = -2.0 + 0.1 * man(sx, sy, ox, oy)

        total = local_best + opp_pen
        if total > best_score:
            best_score = total
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]