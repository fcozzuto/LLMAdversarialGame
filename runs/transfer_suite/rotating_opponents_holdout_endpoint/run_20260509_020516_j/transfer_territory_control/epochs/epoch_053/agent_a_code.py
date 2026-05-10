def choose_move(observation):
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)
    sx, sy = map(int, observation.get("self_position", (0, 0)))
    ox, oy = map(int, observation.get("opponent_position", (0, 0)))

    def to_cells(v):
        s = []
        for p in v or []:
            if p and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                s.append((x, y))
        return s

    obs = set(to_cells(observation.get("obstacles")))
    myT = set(to_cells(observation.get("self_territory")))
    oppT = set(to_cells(observation.get("opponent_territory")))
    unC = to_cells(observation.get("unclaimed_cells"))
    res = to_cells(observation.get("resources"))

    neigh8 = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    neigh8z = neigh8 + [(0, 0)]

    def inb(x, y): return 0 <= x < W and 0 <= y < H
    def free(x, y): return inb(x, y) and (x, y) not in obs

    def adj_to_t(tset, x, y):
        for dx, dy in neigh8:
            if (x + dx, y + dy) in tset:
                return True
        return False

    def man(a, b): return abs(a[0] - b[0]) + abs(a[1] - b[1])

    target = None
    best_td = None
    if myT and unC:
        for ux, uy in unC:
            if free(ux, uy) and adj_to_t(myT, ux, uy):
                d = man((sx, sy), (ux, uy))
                if best_td is None or d < best_td:
                    best_td = d
                    target = (ux, uy)

    if target is None and res:
        target = min((p for p in res if free(p[0], p[1])), key=lambda p: man((sx, sy), p), default=None)

    if target is None:
        if oppT:
            # head toward our nearest approach to opponent territory
            target = min(oppT, key=lambda p: man((sx, sy), p), default=None)

    if target is None:
        # fallback: deterministically bias toward opponent, else stay
        target = (ox, oy)

    best_move = (0, 0)
    best_val = None
    for dx, dy in neigh8z:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        d_to_target = man((nx, ny), target)
        d_to_opp = man((nx, ny), (ox, oy))
        # Prefer getting closer to target; then keep some distance from opponent slightly.
        val = (d_to_target, -d_to_opp, dx, dy)
        if best_val is None or val < best_val:
            best_val = val
            best_move = [dx, dy]
    return best_move