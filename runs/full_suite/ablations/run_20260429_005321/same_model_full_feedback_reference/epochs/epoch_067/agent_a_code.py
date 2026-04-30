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

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    # Pick resource we can reach sooner than opponent; deterministic tie-break.
    target = None
    best_key = None
    for rx, ry in resources:
        selfd = dist2(sx, sy, rx, ry)
        oppd = dist2(ox, oy, rx, ry)
        key = (selfd - oppd, selfd, -rx - ry)  # prefer self closer than opp; then nearer; then deterministic
        if best_key is None or key < best_key:
            best_key = key
            target = (rx, ry)

    if target is None:
        # No visible resources: go towards center while avoiding obstacles deterministically.
        tx, ty = w // 2, h // 2
    else:
        tx, ty = target

    # Choose move that minimizes distance to target; secondary: keep away from opponent; tertiary: deterministic.
    best_move = [0, 0]
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        self_to = dist2(nx, ny, tx, ty)
        opp_to = dist2(nx, ny, ox, oy)
        # Higher opp_to is better (spread). Use lexicographic via negatives.
        score = (self_to, -opp_to, dx, dy)
        if best_score is None or score < best_score:
            best_score = score
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]