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
            ob.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inb(x, y) and (x, y) not in ob

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    cx, cy = (w - 1) // 2, (h - 1) // 2

    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    # obstacle repulsion: avoid squares adjacent to obstacles
    def obs_penalty(x, y):
        p = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (x + dx, y + dy) in ob:
                    p += 1
        return p

    if not resources:
        return [0, 0]

    best_key = None
    best_move = (0, 0)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            nx, ny = sx, sy
            dx, dy = 0, 0

        center_term = md(nx, ny, cx, cy)
        pen = obs_penalty(nx, ny)

        # Choose the resource that maximizes our advantage over opponent.
        # We prefer resources we can reach sooner, and we heavily penalize ones
        # the opponent can reach strictly faster.
        local_best = None
        for r in resources:
            if not r or len(r) < 2:
                continue
            rx, ry = int(r[0]), int(r[1])
            if not valid(rx, ry):
                continue
            myd = md(nx, ny, rx, ry)
            opd = md(ox, oy, rx, ry)

            # score: lower is better
            # advantage_ratio encourages blocking contested resources
            contest = (opd - myd)
            # If opponent is closer, make it much worse.
            opp_closer = 1 if opd < myd else 0
            tie = 1 if opd == myd else 0
            # Also prefer nearer resources overall to reduce drift.
            key = (
                opp_closer * 100 + tie * 10,
                myd,
                -contest,
                center_term,
                pen
            )
            if local_best is None or key < local_best:
                local_best = key

        key_overall = local_best if local_best is not None else (10**9, 10**9, 0, center_term, pen)
        if best_key is None or key_overall < best_key:
            best_key = key_overall
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]