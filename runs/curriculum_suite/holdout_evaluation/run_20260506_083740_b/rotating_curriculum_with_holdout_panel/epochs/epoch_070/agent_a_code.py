def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    ob = set()
    for p in obstacles:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                ob.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inb(x, y) and (x, y) not in ob

    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    cx, cy = (w - 1) // 2, (h - 1) // 2

    # Choose a target resource by who is closer (favor denying opponent).
    best_r = None
    best_key = None
    for r in resources:
        if not r or len(r) < 2:
            continue
        rx, ry = int(r[0]), int(r[1])
        if not valid(rx, ry):
            continue
        sd = md(sx, sy, rx, ry)
        od = md(ox, oy, rx, ry)
        # Higher means better: we prefer resources we can reach first; otherwise we prefer those far from us but close to opponent (deny).
        key = (od - sd, -sd, -rx, -ry)
        if best_key is None or key > best_key:
            best_key = key
            best_r = (rx, ry)

    if best_r is None:
        # No reachable resources: head to center, avoiding obstacles.
        tx, ty = cx, cy
        best_key = None
        best_mv = (0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            key = (-md(nx, ny, tx, ty), -nx, -ny)
            if best_key is None or key > best_key:
                best_key = key
                best_mv = (dx, dy)
        return [best_mv[0], best_mv[1]]

    rx, ry = best_r

    # Evaluate one-step moves by estimated advantage on the chosen target and a secondary denial score.
    best_mv = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        self_d = md(nx, ny, rx, ry)
        opp_d = md(ox, oy, rx, ry)
        # Secondary: after moving, how good is denying other resources around (choose nearest opponent resources).
        denom = 1
        sec = 0
        for r in resources:
            if not r or len(r) < 2:
                continue
            ax, ay = int(r[0]), int(r[1])
            if not valid(ax, ay):
                continue
            od = md(ox, oy, ax, ay)
            if od < 2 * self_d + 2:  # focus on contested ones
                sec = max(sec, od - md(nx, ny, ax, ay))
        score = (opp_d - self_d, sec, -self_d, -abs(nx - rx) - abs(ny - ry), -dx, -dy)
        if best_score is None or score > best_score:
            best_score = score
            best_mv = (dx, dy)

    return [int(best_mv[0]), int(best_mv[1])]