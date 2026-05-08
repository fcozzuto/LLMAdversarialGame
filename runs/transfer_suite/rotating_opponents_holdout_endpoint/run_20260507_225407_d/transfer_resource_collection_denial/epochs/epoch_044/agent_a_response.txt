def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obs.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inb(x, y) and (x, y) not in obs

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_t = None
    best_sc = None

    for r in resources:
        if not (isinstance(r, (list, tuple)) and len(r) == 2):
            continue
        tx, ty = r[0], r[1]
        if not inb(tx, ty) or (tx, ty) in obs:
            continue
        ds = abs(sx - tx) + abs(sy - ty)
        do = abs(ox - tx) + abs(oy - ty)
        sc = (do - ds) * 120 - ds * 3 - do * 1
        if observation.get("turns_remaining") is not None:
            tr = observation["turns_remaining"]
            sc += (tr % 3) - (ds > tr)
        if best_sc is None or sc > best_sc or (sc == best_sc and (tx, ty) < best_t):
            best_sc, best_t = sc, (tx, ty)

    if best_t is None:
        # fallback: deterministically move toward open center-ish
        target = (w // 2, h // 2)
    else:
        target = best_t

    tx, ty = target
    best_move = (0, 0)
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        nd = abs(nx - tx) + abs(ny - ty)
        # Prefer moves that keep us closer than opponent to the target (when possible)
        od = abs(ox - tx) + abs(oy - ty)
        key = (-1 if nd <= od else 0, -nd, nx, ny)
        if best_key is None or key > best_key:
            best_key, best_move = key, (dx, dy)

    dx, dy = best_move
    return [int(dx), int(dy)]