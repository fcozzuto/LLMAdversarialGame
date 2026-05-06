def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", (0, 0)) or (0, 0)
    op = observation.get("opponent_position", (0, 0)) or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def dist(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # Resource selection: prefer resources where we are closer than opponent by a margin,
    # otherwise still choose something that grows opponent distance while moving us closer.
    best = None
    best_key = None
    for tx, ty in resources:
        myd = dist(sx, sy, tx, ty)
        opd = dist(ox, oy, tx, ty)
        margin = opd - myd  # positive => we are ahead
        # Key: maximize margin; then minimize my distance; then maximize opponent distance
        key = (-margin, myd, -opd)
        if best_key is None or key < best_key:
            best_key = key
            best = (tx, ty)

    tx, ty = best
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best_move = (0, 0)
    best_move_key = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            nx, ny = sx, sy

        myd2 = dist(nx, ny, tx, ty)
        opd2 = dist(ox, oy, tx, ty)
        # Prefer reducing our distance; if tie, prefer making target farther for opponent's position;
        # if still tie, prefer obstacle-safety by avoiding staying still when possible.
        moved = 1 if (nx != sx or ny != sy) else 0
        key = (myd2, -opd2, -moved, dx * dx + dy * dy)
        if best_move_key is None or key < best_move_key:
            best_move_key = key
            best_move = (nx - sx, ny - sy)

    return [int(best_move[0]), int(best_move[1])]