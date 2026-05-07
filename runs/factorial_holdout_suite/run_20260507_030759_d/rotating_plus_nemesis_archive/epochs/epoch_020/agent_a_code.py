def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obst = set()
    for p in obstacles:
        try:
            obst.add((int(p[0]), int(p[1])))
        except Exception:
            pass

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    if not resources:
        return [0, 0]

    best_t = None
    best_sc = -10**18
    for r in resources:
        tx, ty = int(r[0]), int(r[1])
        ds = md(sx, sy, tx, ty)
        do = md(ox, oy, tx, ty)
        sc = (do - ds) * 1000 - ds + (do - ds) // 2
        if sc > best_sc:
            best_sc = sc
            best_t = (tx, ty)

    tx, ty = best_t

    cur_ds = md(sx, sy, tx, ty)
    best_mv = (0, 0)
    best_mv_sc = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obst:
            # If invalid/obstacle, staying will typically be chosen via scoring.
            continue
        ns_ds = md(nx, ny, tx, ty)
        ns_do = md(ox, oy, tx, ty)
        # Prefer moves that reduce our distance; also prefer states where opponent is further.
        delta = cur_ds - ns_ds
        sc = delta * 2000 + (ns_do - ns_ds) * 10 - ns_ds
        if (dx, dy) == (0, 0):
            sc -= 1  # small bias to move when safe
        if sc > best_mv_sc:
            best_mv_sc = sc
            best_mv = (dx, dy)

    # If all candidate moves were blocked, fall back deterministically to stay.
    if best_mv == (0, 0) and (sx, sy) in obst:
        return [0, 0]
    return [int(best_mv[0]), int(best_mv[1])]