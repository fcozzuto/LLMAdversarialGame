def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    tr = int(observation.get("turns_remaining", 0))
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    if not resources:
        return [0, 0]

    obs_set = set((x, y) for x, y in obstacles)

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            moves.append((dx, dy))
    moves.sort()

    best = None
    best_key = None
    for rx, ry in sorted(resources):
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        behind = opd - myd
        # Prefer resources we can reach not later than opponent; otherwise still contest if we are less behind.
        lead = myd <= opd
        if not lead and behind > 2 and myd > tr + 6:
            continue
        # Tie-break by being closer, then deterministic by coordinate.
        key = (0 if lead else 1, -(behind if behind > 0 else 0), myd, rx * 8 + ry)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best

    def step_toward(tx, ty, x, y):
        dx = 0 if tx == x else (1 if tx > x else -1)
        dy = 0 if ty == y else (1 if ty > y else -1)
        return dx, dy

    dx, dy = step_toward(tx, ty, sx, sy)
    nx, ny = sx + dx, sy + dy
    if inb(nx, ny) and (nx, ny) not in obs_set:
        return [dx, dy]

    # Obstacle avoidance / slight reroute: pick move that minimizes chebyshev distance to target while not stepping into obstacle.
    best2 = (10**9, None)
    for mdx, mdy in moves:
        nx, ny = sx + mdx, sy + mdy
        if not inb(nx, ny) or (nx, ny) in obs_set:
            continue
        d = cheb(nx, ny, tx, ty)
        key = (d, abs(mdx) + abs(mdy), mdx, mdy)
        if key < best2[0:1]:
            pass
    # Deterministic selection
    chosen = None
    chosen_key = None
    for mdx, mdy in moves:
        nx, ny = sx + mdx, sy + mdy
        if not inb(nx, ny) or (nx, ny) in obs_set:
            continue
        d = cheb(nx, ny, tx, ty)
        k = (d, abs(mdx) + abs(mdy), mdx, mdy)
        if chosen_key is None or k < chosen_key:
            chosen_key = k
            chosen = (mdx, mdy)
    if chosen is None:
        return [0, 0]
    return [chosen[0], chosen[1]]