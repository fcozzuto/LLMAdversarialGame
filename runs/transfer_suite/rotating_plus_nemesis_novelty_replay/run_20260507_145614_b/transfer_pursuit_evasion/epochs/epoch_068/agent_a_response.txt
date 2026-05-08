def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obst = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    role = (observation.get("self_role") or "").lower()
    is_pursuer = ("purs" in role) or ("chaser" in role) or ("capture" in role) or ("pursuer" in role)
    if ("evad" in role) or ("runner" in role):
        is_pursuer = False

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obst

    def score(nx, ny):
        mdx, mdy = nx - ox, ny - oy
        d2 = mdx * mdx + mdy * mdy
        if is_pursuer:
            base = d2  # minimize
            # Prefer moves that reduce the larger component (helps against zigzags)
            reduce = max(abs(mdx), abs(mdy))
            if reduce == 0:
                base -= 1e6
            # Obstacle proximity penalty (avoid getting boxed in)
            prox = 0
            for ax, ay in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                if (nx + ax, ny + ay) in obst:
                    prox += 1
            return base + 2.5 * prox + 0.01 * (abs(nx - sx) + abs(ny - sy)) + 0.001 * reduce
        else:
            base = -d2  # maximize distance => minimize negative
            prox = 0
            for ax, ay in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                if (nx + ax, ny + ay) in obst:
                    prox += 1
            # Prefer moves that increase distance from pursuer; avoid staying still if tied
            still = 1 if (nx == sx and ny == sy) else 0
            return base - 2.5 * prox + 0.02 * still + 0.001 * (abs(nx - ox) + abs(ny - oy))

    best = None
    best_move = [0, 0]
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        sc = score(nx, ny)
        if best is None or sc < best:
            best = sc
            best_move = [dx, dy]

    if best_move == [0, 0]:
        # deterministic fallback: move along axis that increases distance or decreases it, if possible
        candidates = []
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if dx == 0 and dy == 0:
                continue
            if valid(nx, ny):
                mdx, mdy = nx - ox, ny - oy
                candidates.append((mdx * mdx + mdy * mdy, dx, dy))
        if candidates:
            if is_pursuer:
                candidates.sort(key=lambda t: t[0])
            else:
                candidates.sort(key=lambda t: -t[0])
            best_move = [candidates[0][1], candidates[0][2]]

    return [int(best_move[0]), int(best_move[1])]