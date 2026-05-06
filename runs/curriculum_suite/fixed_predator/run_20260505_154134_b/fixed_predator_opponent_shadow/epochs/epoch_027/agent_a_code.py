def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return inb(x, y) and (x, y) not in obs

    if not resources:
        return [0, 0]

    best = None
    best_key = None
    for cx, cy in resources:
        self_d = cheb(sx, sy, cx, cy)
        opp_d = cheb(ox, oy, cx, cy)
        # Favor targets where we are closer than opponent; tie-break by closeness and coordinate
        key = (opp_d - self_d, -self_d, -cx, -cy)
        if best_key is None or key > best_key:
            best_key = key
            best = (cx, cy)
    tx, ty = best

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    opp_d = cheb(ox, oy, tx, ty)
    cur_self_d = cheb(sx, sy, tx, ty)

    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        new_self_d = cheb(nx, ny, tx, ty)
        # Maximize advantage at next step; also strongly prefer reducing distance to chosen target
        adv = opp_d - new_self_d
        progress = cur_self_d - new_self_d
        # Tie-break: prefer smaller distance, then deterministic coordinate order of resulting position
        score = (adv, progress, -new_self_d, -nx, -ny)
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]