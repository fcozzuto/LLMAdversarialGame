def choose_move(observation):
    w = observation.get("grid_width", 0)
    h = observation.get("grid_height", 0)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0),  (0, 0), (1, 0),
             (-1, 1),  (0, 1), (1, 1)]

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def dist(a, b, c, d):
        x = a - c
        if x < 0: x = -x
        y = b - d
        if y < 0: y = -y
        return x + y

    if not resources:
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny): 
                continue
            # Prefer staying, then maximize distance from opponent
            sc = (-(dx == 0 and dy == 0), dist(nx, ny, ox, oy))
            if best is None or sc > best[0] or (sc == best[0] and (dx, dy) < best[1]):
                best = (sc, (dx, dy))
        return list(best[1]) if best else [0, 0]

    # Choose a target resource mostly by how quickly we can reach it vs opponent
    best_r = None
    best_val = None
    for rx, ry in resources:
        d_self = dist(sx, sy, rx, ry)
        d_opp = dist(ox, oy, rx, ry)
        # Prefer where we are closer; tie-break by nearer/deterministic position
        val = (d_opp - d_self, -d_self, (rx, ry))
        if best_val is None or val > best_val:
            best_val = val
            best_r = (rx, ry)
    tx, ty = best_r

    # Evaluate one-step moves by (gain on target) and stealing chances
    best_move = None
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d_t_self = dist(nx, ny, tx, ty)
        d_t_opp = dist(nx, ny, ox, oy)  # proxy: being closer to opponent reduces their access implicitly
        # Steal pressure: do we reduce opponent's advantage on some resource?
        steal = 0
        for rx, ry in resources:
            ds = dist(nx, ny, rx, ry)
            do = dist(ox, oy, rx, ry)
            if ds < do:
                steal += 1
        # Primary: minimize distance to target; Secondary: maximize steal count; Tertiary: avoid giving opponent proximity
        score = (-d_t_self, steal, -d_t_opp, (0 if (dx == 0 and dy == 0) else 1), (dx, dy))
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    if best_move is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]