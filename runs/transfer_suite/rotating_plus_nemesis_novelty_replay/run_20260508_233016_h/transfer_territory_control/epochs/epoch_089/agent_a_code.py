def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    w, h = observation.get("grid_width", 1), observation.get("grid_height", 1)
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    unclaimed = observation.get("unclaimed_cells") or []
    targets = [tuple(c) for c in unclaimed if c is not None]
    if not targets:
        resources = observation.get("resources") or []
        targets = [tuple(c) for c in resources if c is not None]
    if not targets:
        return [0, 0]

    ox, oy = observation.get("opponent_position", (sx, sy))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    best_target = None
    best_score = None
    for tx, ty in targets:
        if not inb(tx, ty):
            continue
        # Prefer near us, but also somewhat away from opponent so we don't walk into their threat.
        score = (md(sx, sy, tx, ty), -md(ox, oy, tx, ty), tx, ty)
        if best_score is None or score < best_score:
            best_score, best_target = score, (tx, ty)
    if best_target is None:
        return [0, 0]
    tx, ty = best_target

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    best_move = None
    best_move_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        # Deterministic: minimize distance to chosen target, tie-break by move direction.
        score = (md(nx, ny, tx, ty), dx, dy)
        if best_move_score is None or score < best_move_score:
            best_move_score, best_move = score, (dx, dy)
    if best_move is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]