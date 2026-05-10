def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    selfT = set()
    for p in observation.get("self_territory", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                selfT.add((x, y))

    oppT = set()
    for p in observation.get("opponent_territory", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                oppT.add((x, y))

    unclaimed = []
    for p in observation.get("unclaimed_cells", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                unclaimed.append((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    # Target selection: favor unclaimed that opponent is less likely to reach first.
    tx, ty = ox, oy
    if unclaimed:
        best = -10**18
        for x, y in unclaimed:
            ds = abs(x - sx) + abs(y - sy)
            do = abs(x - ox) + abs(y - oy)
            # Higher score means better: larger opponent advantage hurts us.
            sc = (do - ds) * 10 - ds
            if (x, y) in selfT:
                sc -= 200
            if sc > best:
                best = sc
                tx, ty = x, y

    # Move evaluation: immediate counterclaim beats everything else; then move toward target.
    best_mv = (0, 0)
    best_sc = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        if (nx, ny) in oppT:
            sc = 10**9  # immediate flipping gain
        else:
            ds_t = abs(tx - nx) + abs(ty - ny)
            ds = abs(tx - sx) + abs(ty - sy)
            do_here = abs(ox - nx) + abs(oy - ny)
            # Prefer reducing distance to target, and avoid giving opponent proximity too much.
            sc = 1000 * (ds - ds_t) + (do_here - abs(ox - sx) - abs(oy - sy)) * 2
            if (nx, ny) in unclaimed:
                sc += 50
            if (nx, ny) in selfT:
                sc -= 5
        if sc > best_sc:
            best_sc = sc
            best_mv = (dx, dy)

    return [int(best_mv[0]), int(best_mv[1])]