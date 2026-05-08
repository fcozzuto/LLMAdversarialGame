def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    obs = observation.get("obstacles", []) or []
    oset = set()
    for p in obs:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            oset.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def legal(nx, ny):
        return inb(nx, ny) and (nx, ny) not in oset

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    srole = str(observation.get("self_role", "")).lower()
    is_pursuer = "purs" in srole

    resources = observation.get("resources", []) or []
    rpts = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rpts.append((int(r[0]), int(r[1])))

    if rpts:
        tx, ty = min(rpts, key=lambda p: abs(p[0] - sx) + abs(p[1] - sy))
        target_is_opponent = False
    else:
        tx, ty = ox, oy
        target_is_opponent = True

    best = None
    best_mv = (0, 0)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        md = abs(nx - tx) + abs(ny - ty)
        if target_is_opponent and not is_pursuer:
            primary = md  # run away
        else:
            primary = -md  # approach target
        # tie-break deterministically by staying still preference then order
        secondary = 0 if (dx, dy) == (0, 0) else 1
        key = (primary, -secondary, -abs(dx) - abs(dy))
        if best is None or key > best:
            best = key
            best_mv = (dx, dy)

    return [int(best_mv[0]), int(best_mv[1])]