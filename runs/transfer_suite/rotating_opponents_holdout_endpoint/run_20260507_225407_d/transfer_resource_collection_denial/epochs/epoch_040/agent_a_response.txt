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

    def manh(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    # Pick target resource with best "intercept" advantage; if none, head to center-left to disrupt.
    best_t = None
    best_key = None
    for r in resources:
        if not (isinstance(r, (list, tuple)) and len(r) == 2):
            continue
        tx, ty = r[0], r[1]
        if not inb(tx, ty) or (tx, ty) in obs:
            continue
        ds = manh(sx, sy, tx, ty)
        do = manh(ox, oy, tx, ty)
        # Prefer we are ahead; if tied, prefer closer; if still tied, prefer more opponent distance.
        key = (-(do - ds), ds, -do, (tx + ty), tx, ty)
        if best_key is None or key < best_key:
            best_key = key
            best_t = (tx, ty)

    if best_t is None:
        tx, ty = (w // 2 - 1 if w > 1 else 0), (h // 2)
    else:
        tx, ty = best_t

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_mkey = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        dself = manh(nx, ny, tx, ty)
        dopp_to_target = manh(ox, oy, tx, ty)
        # Move that reduces our distance first; then makes us closer than opponent to the target next.
        improv = manh(sx, sy, tx, ty) - dself
        # Also lightly prefer moves that increase distance between opponent and our next cell (denier feel).
        d_between = manh(ox, oy, nx, ny)
        mkey = (-improv, dself, -(d_between), nx, ny, dx, dy)
        if best_mkey is None or mkey < best_mkey:
            best_mkey = mkey
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]