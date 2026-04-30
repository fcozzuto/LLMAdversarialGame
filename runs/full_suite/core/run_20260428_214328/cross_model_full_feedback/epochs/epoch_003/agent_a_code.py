def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    occ = obstacles | {(ox, oy)}
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Target selection: prefer resources where we are closer than opponent (maximize do-ds),
    # otherwise fall back to nearest resource.
    tx, ty = None, None
    best_val = None
    best_ds = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        ds = man(sx, sy, rx, ry)
        do = man(ox, oy, rx, ry)
        val = do - ds
        if best_val is None:
            best_val, best_ds, tx, ty = val, ds, rx, ry
        else:
            if val > best_val or (val == best_val and (ds < best_ds or (ds == best_ds and (rx, ry) < (tx, ty)))):
                best_val, best_ds, tx, ty = val, ds, rx, ry

    if tx is None:
        # No valid resources; move to keep distance from opponent deterministically.
        best = (0, 0, 10**9, (0, 0))
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny) or (nx, ny) in obstacles:
                continue
            dso = man(nx, ny, ox, oy)
            # maximize distance; tie by deterministic move preference (dx,dy)
            if dso > best[2] or (dso == best[2] and (dx, dy) < best[3]):
                best = (dx, dy, dso, (dx, dy))
        return [best[0], best[1]]

    # Move scoring towards target while denying opponent progress.
    # Utility = (opp_distance - self_distance) after move, tie-break by smaller self_distance and move coords.
    best_move = (0, 0)
    best_util = -10**18
    best_selfd = 10**18
    best_move_coord = (0, 0)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in occ:
            continue
        selfd = man(nx, ny, tx, ty)
        oppd = man(ox, oy, tx, ty)
        util = (oppd - selfd)
        if util > best_util or (util == best_util and (selfd < best_selfd or (selfd == best_selfd and (dx, dy) < best_move_coord))):
            best_util = util
            best_selfd = selfd
            best_move = (dx, dy)
            best_move_coord = (dx, dy)

    return [best_move[0], best_move[1]]