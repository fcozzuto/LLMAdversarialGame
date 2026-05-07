def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)

    def ti(v):
        try:
            return int(v)
        except:
            return 0

    sx, sy, ox, oy = ti(sx), ti(sy), ti(ox), ti(oy)

    obs = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = ti(p[0]), ti(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = observation.get("resources", []) or []
    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    # Deterministic target: prefer resources we can reach first (or deny best when not)
    best = None
    best_key = None
    for r in resources:
        if not (isinstance(r, (list, tuple)) and len(r) >= 2):
            continue
        tx, ty = ti(r[0]), ti(r[1])
        if not inb(tx, ty) or (tx, ty) in obs:
            continue
        sd = dist(sx, sy, tx, ty)
        od = dist(ox, oy, tx, ty)
        # If tied/behind, go for the one where we lose the least (strongest denial).
        # Tie-break deterministically by coordinates.
        key = (0 if sd <= od else 1, -((od - sd)), sd, tx, ty)
        if best_key is None or key < best_key:
            best_key = key
            best = (tx, ty)

    tx, ty = best

    # Move choice: greedy step toward target; avoid obstacles; deterministic tie-break
    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0),  (0, 0),  (1, 0),
             (-1, 1),  (0, 1),  (1, 1)]
    best_move = (0, 0)
    best_mkey = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        nd = dist(nx, ny, tx, ty)
        # Prefer shortest distance to target; then prefer reducing opponent distance to that target (deny);
        # then deterministic by (dx,dy).
        od = dist(ox, oy, tx, ty)
        mkey = (nd, dist(nx, ny, tx, ty) - dist(sx, sy, tx, ty), -dist(ox, oy, tx, ty), dx, dy)
        if best_mkey is None or mkey < best_mkey:
            best_mkey = mkey
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]