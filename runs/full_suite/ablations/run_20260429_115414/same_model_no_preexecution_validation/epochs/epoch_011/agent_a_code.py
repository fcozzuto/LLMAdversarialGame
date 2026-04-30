def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs_set = set((int(a), int(b)) for a, b in obstacles)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def legal(x, y):
        return inb(x, y) and (x, y) not in obs_set

    def obstacle_pen(x, y):
        if not obstacles:
            return 0
        best = 10**9
        for ax, ay in obstacles:
            d = cheb(x, y, int(ax), int(ay))
            if d < best:
                best = d
                if best == 0:
                    return 10**7
        # discourage being very close to obstacles (force different routes vs last epoch)
        if best == 0:
            return 10**7
        if best == 1:
            return 30
        if best == 2:
            return 10
        if best == 3:
            return 4
        return 0

    # Choose target deterministically: prefer resources where we are not behind,
    # otherwise deny resources where opponent is significantly ahead.
    target = None
    best_key = None
    for rx, ry in resources:
        rx, ry = int(rx), int(ry)
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        ahead = opd - myd  # positive means we are ahead
        # Prefer being ahead; if none, pick where opponent is very ahead (most denial pressure)
        key = (0 if ahead >= 0 else 1, -ahead, myd, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            target = (rx, ry)

    if target is None:
        target = (ox, oy)

    tx, ty = target
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue

        myd = cheb(nx, ny, tx, ty)
        opd = cheb(ox, oy, tx, ty)

        # Score: reduce our distance to target, and increase opponent disadvantage.
        # Also add slight tie-break toward moving away from opponent when contesting.
        myd_now = cheb(sx, sy, tx, ty)
        if myd < myd_now:
            pace_bonus = 6
        elif myd == myd_now:
            pace_bonus = 2
        else:
            pace_bonus = -4

        # Denial: if we are behind, try to shrink the gap quickly
        gap_now = cheb(sx, sy, tx, ty) - cheb(ox, oy, tx, ty)
        gap_new = myd - opd
        gap_improve = -gap_new + (0.5 * (-gap_now))

        # Move away from opponent if we can't get ahead
        opp_close = cheb(nx, ny, ox, oy)
        away_bonus = 0
        if cheb(ox, oy, tx, ty) <= cheb(sx, sy, tx, ty):
            away_bonus = opp_close

        s = (-myd * 18) + (gap_improve * 10) + pace_bonus + away_bonus - obstacle_pen(nx, ny)

        # If target cell is adjacent and we are already not worse, encourage stepping onto it
        if (nx, ny) == (tx, ty):
            s += 10**6

        if s > best_score or (s == best_score and (dx, dy) < best_move):