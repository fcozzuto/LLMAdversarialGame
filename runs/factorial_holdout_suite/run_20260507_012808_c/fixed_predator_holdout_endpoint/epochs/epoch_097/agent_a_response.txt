def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    resources = observation.get("resources") or []
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
    R = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                R.append((x, y))
    if not R:
        return [0, 0]

    cand = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                cand.append((dx, dy, nx, ny))
    if not cand:
        return [0, 0]

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def cell_is_resource(x, y):
        for rx, ry in R:
            if rx == x and ry == y:
                return True
        return False

    # Denial-aware target: prefer resources where we're not worse than opponent.
    # Also bias toward blocking by moving to positions that keep us closer to the opponent's nearest resource.
    opp_target = min(R, key=lambda c: dist((ox, oy), c))
    opp_td0 = dist((ox, oy), opp_target)

    best = None
    best_sc = -10**18
    for dx, dy, nx, ny in cand:
        # primary: race advantage on the best "winnable" resource
        best_adv = -10**18
        best_base_d = 10**9
        for rx, ry in R:
            myd = dist((nx, ny), (rx, ry))
            opd = dist((ox, oy), (rx, ry))
            # if we can be closer than opponent, it should dominate
            adv = (opd - myd)
            if adv > best_adv or (adv == best_adv and myd < best_base_d):
                best_adv = adv
                best_base_d = myd

        # secondary: denial pressure on opponent's current nearest resource
        myd_opp = dist((nx, ny), opp_target)
        denial = (opp_td0 - myd_opp)  # positive means we are moving to it more than opponent baseline

        # tertiary: avoid wasting moves; prefer shorter path to chosen advantages
        score = best_adv * 50 + denial * 10 - best_base_d

        # if stepping directly onto a resource, ensure it's top priority
        if cell_is_resource(nx, ny):
            score += 10**6

        if score > best_sc or (score == best_sc and (dx, dy) < (best[0], best[1]) if best else True):
            best_sc = score
            best = (dx, dy, nx, ny)

    return [int(best[0]), int(best[1])]