def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for o in obstacles:
        if isinstance(o, (list, tuple)) and len(o) == 2:
            x, y = o[0], o[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]

    def manhattan(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    best = None
    best_move = (0, 0)
    # Prefer a move that gives self strong "advantage" over opponent for the nearest contested resource,
    # with a small incentive to hinder opponent when self advantage is similar.
    for dx, dy, nx, ny in moves:
        self_best = 10**9
        opp_best = 10**9
        # Track best resource by self advantage (opp time vs self time).
        best_adv = -10**9
        second = 10**9
        for r in resources:
            if not (isinstance(r, (list, tuple)) and len(r) == 2):
                continue
            rx, ry = r[0], r[1]
            if not (isinstance(rx, int) and isinstance(ry, int)):
                continue
            if not valid(rx, ry):
                continue
            sd = manhattan(nx, ny, rx, ry)
            od = manhattan(ox, oy, rx, ry)
            # advantage > 0 means self is closer (fewer steps).
            adv = od - sd
            if adv > best_adv:
                best_adv = adv
                self_best = sd
                opp_best = od
            elif adv == best_adv and sd < self_best:
                self_best = sd
                opp_best = od

        # If no resources (or all invalid), just drift away from opponent to reduce their access.
        if resources:
            # Main objective: maximize advantage; secondary: minimize self distance; tertiary: maximize opponent distance.
            # Also add a mild penalty for moves that approach opponent too much when advantage is low.
            opp_d = manhattan(nx, ny, ox, oy)
            key = (best_adv, -self_best, opp_d, -(self_best + 2 * (8 - (opp_best if opp_best < 10**8 else 0))))
        else:
            opp_d = manhattan(nx, ny, ox, oy)
            key = (opp_d, -manhattan(nx, ny, sx, sy))
        if best is None or key > best:
            best = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]