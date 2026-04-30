def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def d2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        tx = 0 if sx + ox <= (w - 1) else (w - 1)
        ty = 0 if sy + oy <= (h - 1) else (h - 1)
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if ok(nx, ny):
                key = (d2(nx, ny, tx, ty), d2(ox, oy, nx, ny), dx, dy)
                if best is None or key < best[0]:
                    best = (key, (dx, dy))
        return best[1] if best else [0, 0]

    # Greedy lookahead: maximize "opponent distance advantage" for the best reachable resource after this move.
    best_move = (0, 0)
    best_score = None
    best_tiebreak = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        # Compute best advantage among all resources.
        # Prefer making the gap (opp_dist - self_dist) large; break ties by closer to a resource and farther from opponent.
        advantage = None
        close_self = None
        for rx, ry in resources:
            selfd = d2(nx, ny, rx, ry)
            oppd = d2(ox, oy, rx, ry)
            gap = oppd - selfd
            if advantage is None or gap > advantage or (gap == advantage and selfd < close_self):
                advantage = gap
                close_self = selfd
        # If advantage is negative for all, still choose the move that minimizes our distance to the resource the opponent is also nearest to.
        if best_score is None:
            best_score = advantage
            best_move = (dx, dy)
            best_tiebreak = (close_self, -d2(nx, ny, ox, oy), dx, dy)
        else:
            tb = (close_self, -d2(nx, ny, ox, oy), dx, dy)
            if advantage > best_score or (advantage == best_score and tb < best_tiebreak):
                best_score = advantage
                best_move = (dx, dy)
                best_tiebreak = tb

    return [int(best_move[0]), int(best_move[1])]