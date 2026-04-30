def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist(a, b, c, d):
        return abs(a - c) + abs(b - d)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    dirs2 = [d for d in dirs if d != (0, 0)] + [(0, 0)]

    # Pick best target resource: maximize opponent advantage (opp faster than self).
    if resources:
        best = None
        for rx, ry in resources:
            ds = dist(sx, sy, rx, ry)
            do = dist(ox, oy, rx, ry)
            adv = do - ds
            # Tie-break: prefer smaller ds, then higher total reach, then lexicographic.
            key = (adv, -ds, -(ds + do), -rx, -ry)
            if best is None or key > best[0]:
                best = (key, rx, ry)
        _, tx, ty = best
    else:
        # No resources visible: move toward opponent side's center-ish deterministically.
        tx, ty = (w // 2, h // 2)

    # Greedy step toward target, but choose move that maximizes (adv after move).
    best_move = (0, 0)
    best_score = None
    for dx, dy in dirs2:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        if resources:
            # Evaluate advantage at next position with the chosen target and also nearby resources.
            # Keep it light: mostly follow chosen target, slight bias to nearest overall.
            ds = dist(nx, ny, tx, ty)
            do = dist(ox, oy, tx, ty)
            score = (do - ds, -ds, -dist(nx, ny, ox, oy), dx, dy)
            # Small secondary: if target is far, also consider any resource within 6 manhattan.
            close = None
            for rx, ry in resources:
                if dist(nx, ny, rx, ry) <= 6:
                    if close is None or dist(nx, ny, rx, ry) < close[0]:
                        close = (dist(nx, ny, rx, ry), rx, ry)
            if close is not None:
                cd, crx, cry = close
                score = (score[0], score[1], score[2], -cd, -crx, -cry, dx, dy)
        else:
            score = (-dist(nx, ny, tx, ty), -dist(nx, ny, ox, oy), dx, dy)

        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]