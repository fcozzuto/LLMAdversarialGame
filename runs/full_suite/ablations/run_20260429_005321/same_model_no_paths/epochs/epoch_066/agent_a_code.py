def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Pick a promising target deterministically: best from our perspective, accounting for opponent.
    best_targets = []
    best_key = None
    for rx, ry in resources:
        d_self = cheb(sx, sy, rx, ry)
        d_opp = cheb(ox, oy, rx, ry)
        contest = 1 if d_self <= d_opp else 0
        # Prefer contestable closer targets; tie-break by larger opp disadvantage and then coordinates.
        key = (contest, -d_self, d_opp - d_self, -rx, -ry)
        if best_key is None or key > best_key:
            best_key = key
            best_targets = [(rx, ry)]
        elif key == best_key:
            best_targets.append((rx, ry))
    # Deterministic tie-break among targets
    tx, ty = min(best_targets, key=lambda p: (p[0], p[1]))

    # Evaluate moves by resulting advantage to the target and immediate safety from obstacles.
    best_move = [0, 0]
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            nx, ny = sx, sy
        d_self = cheb(nx, ny, tx, ty)
        d_opp = cheb(ox, oy, tx, ty)
        contest = 1 if d_self <= d_opp else 0

        # Micro-safety: count available neighbors from new pos (prefer more mobility).
        mob = 0
        for ax, ay in dirs:
            px, py = nx + ax, ny + ay
            if valid(px, py):
                mob += 1

        # Additional deterministic tiebreak: avoid stepping away from target diagonally/orthogonally.
        step_toward = 1 if cheb(nx, ny, tx, ty) < cheb(sx, sy, tx, ty) else 0

        val = (contest, step_toward, -d_self, d_opp - d_self, mob, -abs(nx - tx) - abs(ny - ty), dx, dy)
        if best_val is None or val > best_val:
            best_val = val
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]