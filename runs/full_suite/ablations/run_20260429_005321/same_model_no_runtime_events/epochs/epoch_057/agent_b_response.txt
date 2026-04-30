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

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if ok(x, y):
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def md(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    if not ok(sx, sy):
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if ok(nx, ny):
                return [dx, dy]
        return [0, 0]

    if resources:
        best_r = resources[0]
        best_val = 10**9
        for rx, ry in resources:
            ds = md(sx, sy, rx, ry)
            do = md(ox, oy, rx, ry)
            # Prefer resources we are closer to; strongly avoid letting opponent be equally/closer
            val = ds + 2.2 * (1.0 / (do + 1))
            if val < best_val:
                best_val = val
                best_r = (rx, ry)

        rx, ry = best_r
        best_move = [0, 0]
        best_score = 10**9
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            ds2 = md(nx, ny, rx, ry)
            do2 = md(ox, oy, rx, ry)
            # Also lightly discourage moves that reduce opponent's chance by keeping us closer while worsening opponent proximity balance
            score = ds2 + 2.2 * (1.0 / (do2 + 1))
            # If tied, prefer not staying
            if score < best_score or (score == best_score and (dx != 0 or dy != 0)):
                best_score = score
                best_move = [dx, dy]
        return best_move

    # No visible resources: reposition toward center while staying away from opponent
    cx, cy = w // 2, h // 2
    best_move = [0, 0]
    best_score = -10**9
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        dc = -md(nx, ny, cx, cy)  # closer to center is better
        dp = md(nx, ny, ox, oy)  # farther from opponent is better
        score = 0.9 * dc + 0.4 * dp
        if score > best_score or (score == best_score and (dx != 0 or dy != 0)):
            best_score = score
            best_move = [dx, dy]
    return best_move