def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw = observation.get("grid_width", 8)
    gh = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = {tuple(p) for p in obs_list}

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    def dist(ax, ay, bx, by):
        d = abs(ax - bx) + abs(ay - by)
        if ax == bx and ay == by:
            return -1  # reward collecting
        return d

    if not resources:
        return [0, 0]

    # Pick a target: prefer resources we are closer to; if none, pick one opponent is closer to (intercept).
    scored = []
    for rx, ry in resources:
        ds = dist(sx, sy, rx, ry)
        do = dist(ox, oy, rx, ry)
        if ds < 0:
            scored.append((-10_000, rx, ry))
            continue
        # ds/do gap: larger positive means we are closer.
        gap = do - ds
        scored.append((-(gap) if gap <= 0 else -gap, rx, ry))
    # Deterministic: choose best by (flag, x, y) via sorting key.
    scored.sort(key=lambda t: (t[0], t[1], t[2]))
    _, tx, ty = scored[0]

    # Move decision: minimize distance to target while avoiding obstacles and penalizing moves that allow opponent to be much closer.
    best = (10**9, 0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue

        d_to = dist(nx, ny, tx, ty)
        if d_to < 0:
            return [dx, dy]

        # Obstacle proximity penalty (deterministic small weight)
        pen = 0
        for ex, ey in obstacles:
            dd = abs(nx - ex) + abs(ny - ey)
            if dd == 0:
                pen += 1000
            elif dd == 1:
                pen += 4
            elif dd == 2:
                pen += 1

        # Opponent response: predict if they are closer to this target than we are after our move.
        opp_d = dist(ox, oy, tx, ty)
        my_after = dist(nx, ny, tx, ty)
        contest = 0
        if my_after >= 0 and opp_d >= 0:
            gap = opp_d - my_after
            if gap > 0:
                contest += 2 * gap  # if we are farther, make it worse
            else:
                contest += -1 * gap  # if we are closer, slightly better

        # Tie-breaker by deterministic ordering via dx,dy
        key = (d_to + pen + contest, abs(tx - nx) + abs(ty - ny), dx, dy)
        if key < best:
            best = (key[0], dx, dy)

    return [best[1], best[2]]