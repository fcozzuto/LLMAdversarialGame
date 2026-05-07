def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    obs = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))
    resources = []
    for r in (observation.get("resources") or []):
        if r and len(r) >= 2:
            resources.append((int(r[0]), int(r[1])))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def md(a, b):
        dx = a[0] - b[0]
        if dx < 0: dx = -dx
        dy = a[1] - b[1]
        if dy < 0: dy = -dy
        return dx + dy

    def close_to_obstacle(x, y):
        p = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                if (x + ax, y + ay) in obs:
                    p += 1
        return p

    if not resources:
        # drift away from opponent if possible, otherwise head toward them
        dx = 0
        if sx < ox and inside(sx + 1, sy): dx = 1
        elif sx > ox and inside(sx - 1, sy): dx = -1
        dy = 0
        if sy < oy and inside(sx, sy + 1): dy = 1
        elif sy > oy and inside(sx, sy - 1): dy = -1
        if dx == 0 and dy == 0:
            return [0, 0]
        return [dx, dy]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    # pick a target resource where we are relatively closer than opponent
    best_target = resources[0]
    best_gap = -10**9
    for t in resources:
        gap = md((ox, oy), t) - md((sx, sy), t)
        if t == (sx, sy):
            gap += 1000
        # also prefer central-ish routes when gap similar
        tie = -md(t, (w // 2, h // 2)) * 0.01
        score = gap + tie
        if score > best_gap:
            best_gap = score
            best_target = t

    tx, ty = best_target
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        d0 = md((nx, ny), (tx, ty))
        d1_self = md((nx, ny), (tx, ty))
        d1_opp = md((ox, oy), (tx, ty))
        on_resource = 1 if (nx, ny) in obs else 0
        own_gain = 1 if (nx, ny) == (tx, ty) else 0
        # prefer moving closer, winning the race, and not bumping near obstacles
        val = -d1_self + 0.9 * (d1_opp - d1_self) + 6 * own_gain - 0.35 * close_to_obstacle(nx, ny)
        # slight preference to not overcommit diagonally when aligned
        if dx != 0 and dy != 0:
            val -= 0.05
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]