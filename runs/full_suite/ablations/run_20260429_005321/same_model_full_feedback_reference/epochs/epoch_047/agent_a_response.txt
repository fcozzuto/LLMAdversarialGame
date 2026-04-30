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

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist2(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        return dx * dx + dy * dy

    # Interference-first: target a resource the opponent is currently closest to.
    best_enemy = None
    best_enemy_d = None
    for tx, ty in resources:
        d = dist2(ox, oy, tx, ty)
        if best_enemy_d is None or d < best_enemy_d or (d == best_enemy_d and (tx, ty) < best_enemy):
            best_enemy_d = d
            best_enemy = (tx, ty)
    tx, ty = best_enemy if best_enemy is not None else (sx, sy)

    # Fallback: if no resources, retreat towards corner opposite opponent.
    if best_enemy is None:
        tx = 0 if ox > (w - 1) / 2 else (w - 1)
        ty = 0 if oy > (h - 1) / 2 else (h - 1)

    best_move = (0, 0)
    best_score = None

    # Score moves: deny opponent's progress to chosen interference resource; also keep some distance.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        d_self = dist2(nx, ny, tx, ty)
        d_opp = dist2(ox, oy, tx, ty)
        # If opponent is closer, prefer moves that reduce that gap (deny capture).
        gap = d_opp - d_self

        # Also consider general resource collection: nearest resource to new position.
        nearest_self = None
        nearest_opp = None
        for rx, ry in resources:
            ds = dist2(nx, ny, rx, ry)
            if nearest_self is None or ds < nearest_self:
                nearest_self = ds
            do = dist2(ox, oy, rx, ry)
            if nearest_opp is None or do < nearest_opp:
                nearest_opp = do

        # Prefer survival: keep distance from opponent.
        sep = dist2(nx, ny, ox, oy)

        # Deterministic tie-breaking: lexicographic on (score, move).
        score = 0
        if resources:
            # Higher is better: deny gap + advantage on nearest resource + separation.
            score = gap * 5 + (nearest_opp - nearest_self) * 2 + sep
        else:
            score = gap * 5 + sep

        if best_score is None or score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    dx, dy = best_move
    return [int(dx), int(dy)]