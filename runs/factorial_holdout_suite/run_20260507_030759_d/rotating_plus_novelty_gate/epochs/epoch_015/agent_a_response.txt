def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obs_list)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    legal = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                legal.append((dx, dy))
    if not legal:
        return [0, 0]

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    if not resources:
        best = None
        bestv = None
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            v = -man(nx, ny, ox, oy)
            k = (v, nx, ny)
            if bestv is None or k > bestv:
                bestv = k
                best = (dx, dy)
        return [best[0], best[1]]

    # Interception-oriented: for each move, maximize "catch advantage" on a small deterministic set of target resources.
    opp_to_res = {tuple(r): man(ox, oy, r[0], r[1]) for r in resources}
    res_sorted = sorted(resources, key=lambda r: (man(sx, sy, r[0], r[1]), r[0], r[1]))
    targets = res_sorted[:8]

    best = (0, 0)
    best_key = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        our_to_res = []
        for r in targets:
            rx, ry = r
            our_d = man(nx, ny, rx, ry)
            opp_d = opp_to_res[(rx, ry)]
            # Main term: how much sooner we can arrive than the opponent.
            catch = opp_d - our_d
            # Secondary: prefer moves that reduce absolute distance to good catches.
            our_to_res.append((catch, -our_d, rx, ry))
        # Deterministically pick best resource outcome for this move.
        our_to_res.sort(reverse=True)
        top = our_to_res[0]
        catch, neg_our_d, rx, ry = top

        # Small tie-break to influence sweeping opponents: keep reducing distance to opponent (intercept pressure).
        v_intercept = -man(nx, ny, ox, oy) // 2

        key = (catch, neg_our_d, v_intercept, -abs(nx - rx) - abs(ny - ry), nx, ny)
        if best_key is None or key > best_key:
            best_key = key
            best = (dx, dy)
    return [best[0], best[1]]