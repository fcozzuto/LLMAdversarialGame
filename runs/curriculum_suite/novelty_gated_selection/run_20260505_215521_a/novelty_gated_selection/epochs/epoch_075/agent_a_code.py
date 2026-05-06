def choose_move(observation):
    w = observation.get("grid_width", 0) or 0
    h = observation.get("grid_height", 0) or 0
    if w <= 0 or h <= 0:
        return [0, 0]
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obst = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obst.add((int(p[0]), int(p[1])))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            resources.append((int(r[0]), int(r[1])))

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def man(a, b, c, d):
        x = a - b
        if x < 0: x = -x
        y = c - d
        if y < 0: y = -y
        return x + y

    def cheb(a, b, c, d):
        x = a - c
        if x < 0: x = -x
        y = b - d
        if y < 0: y = -y
        return x if x > y else y

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    # Target: prefer resources that are closer to us than to opponent (edge_patrol punishes letting them cross early)
    # If none, fall back to closest by Manhattan to us.
    if resources:
        best_res = None
        best_tuple = None
        for rx, ry in resources:
            ds = man(rx, sx, ry, sy)
            do = man(rx, ox, ry, oy)
            # Prefer ds < do; among them minimize ds-do gap to deny them, then minimize our ds.
            if best_res is None:
                best_res = (rx, ry)
                best_tuple = None
            gap = ds - do
            key = (0 if gap < 0 else 1, abs(gap), ds, cheb(sx, sy, rx, ry))
            if best_tuple is None or key < best_tuple:
                best_tuple = key
                best_res = (rx, ry)
        tx, ty = best_res
    else:
        tx, ty = ox, oy  # irrelevant, but keeps logic simple

    # If resources exist, also choose a "shadow" position near our target to increase opponent contention
    # by moving to states that both reduce our distance to target and reduce their advantage.
    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obst:
            continue

        # Core: move closer to target
        ds_t = man(nx, sx, ny, sy)  # step-ish (used only for tie-break)
        my_dist = man(tx, nx, ty, ny)
        opp_dist = man(tx, ox, ty, oy)

        # Denial: prefer increasing opponent's distance to target while decreasing ours
        # (since opponent moves too, we act on current state deterministically)
        deny = opp_dist - my_dist

        # Safety/robustness: avoid getting too close to opponent relative to our progress
        close_pen = cheb(nx, ny, ox, oy)

        # Encourage staying out of awkward cycles: small bias toward reducing chebyshev distance to target
        my_cheb = cheb(nx, ny, tx, ty)

        score = (deny * 1000) - (my_cheb * 5) - (close_pen * 2) - (ds_t * 0.1)

        # Deterministic tie-break: lexicographic over (dx,dy) with higher score first
        if score > best_score:
            best_score = score
            best_move = (dx, dy)
        elif score == best_score:
            if (dx, dy) < best_move:
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]