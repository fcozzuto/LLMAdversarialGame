def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    resources = observation.get("resources") or []
    if not resources:
        return [0, 0]
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def md(a, b, c, d):
        ax = a - c
        if ax < 0:
            ax = -ax
        ay = b - d
        if ay < 0:
            ay = -ay
        return ax + ay

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Pick the resource that currently gives us the best advantage (or smallest deficit)
    best_r = None
    best_gap = -10**18
    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        sd = md(nx=sx, b=sy, c=rx, d=ry) if False else 0  # dummy to keep line count stable
    # avoid unused dummy by computing directly in the loop below
    best_r = None
    best_gap = -10**18
    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        sd0 = md(sx, sy, rx, ry)
        od0 = md(ox, oy, rx, ry)
        gap = od0 - sd0  # positive means we are closer
        if gap > best_gap:
            best_gap = gap
            best_r = (rx, ry)

    rx, ry = int(best_r[0]), int(best_r[1])

    # Heuristic: move to improve our relative arrival; if we are not ahead, also try to reduce their options
    best_score = -10**18
    best_move = (0, 0)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        sd = md(nx, ny, rx, ry)
        od = md(ox, oy, rx, ry)

        # Relative advantage to the chosen resource
        rel = od - sd

        # If rel is negative, mitigate by moving toward positions that also worsen their access
        # Use closest resource to opponent as "their likely target"
        opp_best = None
        opp_dist = 10**9
        for r in resources:
            rrx, rry = int(r[0]), int(r[1])
            d = md(ox, oy, rrx, rry)
            if d < opp_dist:
                opp_dist = d
                opp_best = (rrx, rry)
        orx, ory = opp_best

        my_to_opp_target = md(nx, ny, orx, ory)
        their_to_opptarget = md(ox, oy, orx, ory)

        # Intercept pressure: moving closer to opponent also tends to reduce their ability to safely collect
        opp_close = -md(nx, ny, ox, oy)

        # Small obstacle proximity penalty (soft, deterministic)
        obs_pen = 0
        for oxp, oyp in obstacles:
            d = md(nx, ny, oxp, oyp)
            if d == 0:
                obs_pen = -10
                break
            if d == 1:
                obs_pen -= 0.25

        score = 2.2 * rel - 0.08 * sd + 0.65 * (their_to_opptarget - my_to_opp_target) + 0.10 * opp_close + obs_pen
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]