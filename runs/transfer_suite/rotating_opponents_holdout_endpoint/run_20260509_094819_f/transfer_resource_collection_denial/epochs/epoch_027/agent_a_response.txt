def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obst = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    dirs = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if not (dx == 0 and dy == 0)]
    candidates = dirs + [(0, 0)]

    best = (0, 0)
    best_val = -10**18

    # Deterministic tie-break order: iterate candidates in fixed order (dirs then stay).
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue

        # Own next-cell distance to nearest resource; opponent advantage discouragement.
        nd_self = 10**9
        nd_opp = 10**9
        immediate = 0
        for rx, ry in resources:
            ds = abs(nx - rx) + abs(ny - ry)
            do = abs(nx - ox) + abs(ny - oy)  # depends only on nx,ny
            if ds < nd_self:
                nd_self = ds
            if rx == nx and ry == ny:
                immediate = 1
            if do < nd_opp:
                nd_opp = do

        # Better: choose moves that approach resources and reduce opponent pressure.
        val = -nd_self + 0.45 * nd_opp
        # Strongly prefer stepping onto a resource.
        if immediate:
            val += 10**7

        # Second-order: if moving doesn't worsen our closeness to the best resource, favor it.
        # (Uses current vs next distance to nearest resource.)
        cur_best = 10**9
        for rx, ry in resources:
            cur_best = min(cur_best, abs(sx - rx) + abs(sy - ry))
        if nd_self <= cur_best:
            val += 500

        if val > best_val:
            best_val = val
            best = (dx, dy)

    return [int(best[0]), int(best[1])]