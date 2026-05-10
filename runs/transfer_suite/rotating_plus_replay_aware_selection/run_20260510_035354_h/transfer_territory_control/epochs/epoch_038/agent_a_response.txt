def choose_move(observation):
    ax, ay = observation["self_position"]
    w, h = observation["grid_width"], observation["grid_height"]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = observation.get("obstacles") or []
    obs = set((x, y) for x, y in obstacles if inb(x, y))

    unclaimed = observation.get("unclaimed_cells") or []
    my_t = observation.get("self_territory") or []
    op_t = observation.get("opponent_territory") or []

    un_set = set((x, y) for x, y in unclaimed if inb(x, y))
    my_set = set((x, y) for x, y in my_t if inb(x, y))
    op_set = set((x, y) for x, y in op_t if inb(x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Focus target selection deterministically: pick nearest "frontier" unclaimed cell
    candidates = []
    for x, y in un_set:
        # only consider cells near opponent or near boundary of our territory
        d_op = 10
        for ox, oy in op_set:
            d = md(x, y, ox, oy)
            if d < d_op:
                d_op = d
                if d_op == 1:
                    break
        if d_op <= 3:
            candidates.append((d_op, md(x, y, ax, ay), x, y))
    if not candidates:
        for x, y in un_set:
            # fallback: nearest unclaimed
            candidates.append((md(x, y, ax, ay), 0, x, y))
    candidates.sort()
    # cap targets for speed
    targets = [(c[2], c[3]) for c in candidates[:12]] if candidates else [(ax, ay)]

    best = None
    bestv = None
    for dx, dy in moves:
        nx, ny = ax + dx, ay + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            nx, ny, dx, dy = ax, ay, 0, 0

        # Base gain for taking control
        if (nx, ny) in un_set:
            gain = 12
        elif (nx, ny) in op_set:
            gain = 9
        elif (nx, ny) in my_set:
            gain = 2
        else:
            gain = 1

        # Heuristic: move toward closest target; also slightly avoid moving away from our current territory cluster
        dist_target = min(md(nx, ny, tx, ty) for tx, ty in targets) if targets else 0
        dist_now = min(md(ax, ay, tx, ty) for tx, ty in targets) if targets else 0
        approach = dist_now - dist_target

        # Penalize potential trap: if move reduces liberties (unclaimed neighbors count)
        neigh = 0
        neigh_op = 0
        for ddx in (-1, 0, 1):
            for ddy in (-1, 0, 1):
                if ddx == 0 and ddy == 0:
                    continue
                xx, yy = nx + ddx, ny + ddy
                if inb(xx, yy) and (xx, yy) not in obs:
                    if (xx, yy) in un_set:
                        neigh += 1
                    elif (xx, yy) in op_set:
                        neigh_op += 1
        trap_pen = 0 if neigh >= 2 else (2 - neigh)

        val = gain * 3 + approach * 1.5 + neigh * 0.8 + neigh_op * 0.6 - trap_pen * 1.2 - dist_target * 0.08

        # Deterministic tie-break: prefer non-stay if equal, then lexicographic by (dx,dy)
        key = (val, 1 if (dx != 0 or dy != 0) else 0, -nx - ny, dx, dy)
        if bestv is None or key > bestv:
            bestv = key
            best = (dx, dy)

    return [int(best[0]), int(best[1])]