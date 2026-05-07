def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources") or []
    obstacles_in = observation.get("obstacles") or []
    if not resources:
        return [0, 0]

    obstacles = set()
    for p in obstacles_in:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def blocked(x, y):
        return (x, y) in obstacles

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Pick best resource target by race advantage.
    best_t = None
    best_key = None
    for r in resources:
        tx, ty = int(r[0]), int(r[1])
        sd = man(sx, sy, tx, ty)
        od = man(ox, oy, tx, ty)
        # Prefer secure targets; then maximize (od - sd) and smaller self distance.
        secure = 1 if sd < od else 0
        key = (secure, (od - sd), -sd, -abs(ty - sy))
        if best_key is None or key > best_key:
            best_key = key
            best_t = (tx, ty)

    tx, ty = best_t
    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    # One-step look to improve race; if opponent is close to the target, bias against giving up.
    opp_close = 1 if man(ox, oy, tx, ty) <= 2 else 0

    best_move = None
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or blocked(nx, ny):
            continue
        nsd = man(nx, ny, tx, ty)
        nod = man(ox, oy, tx, ty)
        # Higher is better.
        val = (1 if nsd < nod else 0, (nod - nsd), -nsd)
        # If opponent is close, also prefer moves that reduce distance in the same direction as target.
        if opp_close:
            dir_pref = -man(nx, ny, tx, ty) + -0.5 * abs((tx - nx) - (tx - sx))
            val = (val[0], val[1], val[2], dir_pref)
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    if best_move is None:
        return [0, 0]
    dx, dy = best_move
    return [int(dx), int(dy)]