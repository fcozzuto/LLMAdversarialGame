def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources") or []
    obstacles_in = observation.get("obstacles") or []
    if not resources:
        return [0, 0]

    obstacles = set()
    for p in obstacles_in:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inside(x, y) and (x, y) not in obstacles

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    best = None
    best_key = None
    for r in resources:
        tx, ty = int(r[0]), int(r[1])
        sd = man(sx, sy, tx, ty)
        od = man(ox, oy, tx, ty)
        secure = 1 if sd < od else 0
        # If we can't secure, still pick a target that is least-worse in our race.
        key = (secure, (od - sd), -sd)
        if best_key is None or key > best_key:
            best_key = key
            best = (tx, ty)

    tx, ty = best
    # If stuck (all resources at obstacle positions), stay.
    if not valid(sx, sy):
        return [0, 0]

    def greedy_next(px, py, target_x, target_y):
        bestd = None
        bestm = (0, 0)
        for dx, dy in deltas:
            nx, ny = px + dx, py + dy
            if not valid(nx, ny):
                continue
            d = man(nx, ny, target_x, target_y)
            if bestd is None or d < bestd or (d == bestd and (dx, dy) < bestm):
                bestd = d
                bestm = (dx, dy)
        return bestm

    # Choose our move by minimizing our distance advantage after opponent greedy response.
    best_score = None
    best_move = (0, 0)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d_self = man(nx, ny, tx, ty)
        odx, ody = greedy_next(ox, oy, tx, ty)
        nox, noy = ox + odx, oy + ody
        d_opp = man(nox, noy, tx, ty)

        # Primary: make ourselves closer (smaller d_self), secondary: enlarge our gap (d_opp - d_self),
        # tertiary: keep away from opponent to reduce their ability to contest other nearby resources.
        opp_own = man(nx, ny, nox, noy)
        score = (-d_self, (d_opp - d_self), -opp_own, - (abs(dx) + abs(dy)))
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]