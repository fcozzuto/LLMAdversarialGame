def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obstacles_list)

    def sign(v):
        return 0 if v == 0 else (1 if v > 0 else -1)

    def in_bounds(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def blocked(nx, ny):
        return (nx, ny) in obstacles

    def dist(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    def target_score(tx, ty, px, py):
        d_me = dist(px, py, tx, ty)
        d_opp = dist(ox, oy, tx, ty)
        lead = d_opp - d_me
        return lead * 1000 - d_me + 0.01 * d_opp

    if not resources:
        dx = -sign(ox - x)
        dy = -sign(oy - y)
        return [dx, dy]

    # Pick target that we can contest/secure (best lead, then closer).
    best_tx, best_ty = resources[0][0], resources[0][1]
    best_val = None
    for r in resources:
        tx, ty = r[0], r[1]
        v = target_score(tx, ty, x, y)
        if best_val is None or v > best_val or (v == best_val and (dist(x, y, tx, ty) < dist(x, y, best_tx, best_ty))):
            best_val = v
            best_tx, best_ty = tx, ty

    # Among possible moves, take the one that maximizes future contest value.
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_future = None
    # Simple memory-free "interceptor": also slightly favor moves that reduce distance to the chosen target
    base_d = dist(x, y, best_tx, best_ty)

    for dx, dy in deltas:
        nx, ny = x + dx, y + dy
        if not in_bounds(nx, ny):
            continue
        if blocked(nx, ny):
            continue

        # If blocked in-engine would keep us; we avoid to be robust.
        future = target_score(best_tx, best_ty, nx, ny) - 2.0 * dist(nx, ny, best_tx, best_ty)
        # Small tie-break to keep deterministic "progress": prefer smaller remaining distance, then lexicographic delta.
        rem = dist(nx, ny, best_tx, best_ty)
        cur = (future, -rem, -((nx - x) == 0 and (ny - y) == 0), -dx, -dy)
        if best_future is None:
            best_future = cur
            best_move = (dx, dy)
        else:
            if cur > best_future:
                best_future = cur
                best_move = (dx, dy)

    # Fallback: if all candidate moves were blocked/out-of-bounds, move toward target anyway.
    dx0 = sign(best_tx - x)
    dy0 = sign(best_ty - y)
    if best_move == (0, 0) and not in_bounds(x + dx0, y + dy0):
        dx0 = 0
    if best_move == (0, 0) and not in_bounds(x + dx0, y):
        dy0 = 0
    nx0, ny0 = x + dx0, y + dy0
    if in_bounds(nx0, ny0) and not blocked(nx0, ny0):
        return [dx0, dy0]

    # As last resort, stay.
    return [0, 0]