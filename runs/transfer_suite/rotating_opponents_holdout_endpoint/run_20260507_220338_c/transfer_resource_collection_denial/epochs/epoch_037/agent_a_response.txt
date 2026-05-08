def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    resources = [tuple(r) for r in (observation.get("resources", []) or []) if tuple(r) not in obstacles]
    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    # small deterministic tie-break: prefer moves with smaller distance to best target
    def best_target_for_score():
        best = None
        bestkey = (-10**9, -10**9)
        for rx, ry in resources:
            myd = cheb(sx, sy, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            race = opd - myd
            key = (race, -myd)
            if best is None or key > bestkey:
                best = (rx, ry); bestkey = key
        return best

    bt = best_target_for_score()

    best_val = -10**18
    best_move = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        val = 0.0
        # Evaluate contested resources; pursue ones we can win, contest ones they are closest to.
        for rx, ry in resources:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            race = opd - myd  # >0 means we are closer
            # win term and deny/contest term
            if race >= 0:
                val += 11.0 * race - 0.40 * myd
            else:
                val += 5.5 * race - 0.15 * myd  # race negative: still worth moving if it's highly contested

        # If we can't see many resources, drift toward best current target to avoid aimless dithering
        if len(resources) <= 4 and bt is not None:
            val += -0.25 * cheb(nx, ny, bt[0], bt[1])

        # tie-break: prefer smaller step distance to bt
        if bt is not None:
            tieb = -cheb(nx, ny, bt[0], bt[1])
        else:
            tieb = 0

        cand = (val, tieb)
        best_cand = (best_val, -10**18)
        if cand[0] > best_val:
            best_val = cand[0]
            best_move = (dx, dy)
        elif cand[0] == best_val and cand[1] > best_cand[1]:
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]