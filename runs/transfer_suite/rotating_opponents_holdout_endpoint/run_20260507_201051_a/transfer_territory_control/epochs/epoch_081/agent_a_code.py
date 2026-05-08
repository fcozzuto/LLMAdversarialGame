def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    oppT = observation.get("opponent_territory") or []
    opp_set = set((int(p[0]), int(p[1])) for p in oppT if isinstance(p, (list, tuple)) and len(p) >= 2)

    unclaimed = observation.get("unclaimed_cells") or []
    un_set = set((int(p[0]), int(p[1])) for p in unclaimed if isinstance(p, (list, tuple)) and len(p) >= 2)

    neigh = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    frontier = []
    for ux, uy in un_set:
        for dx, dy in neigh:
            if (ux + dx, uy + dy) in opp_set:
                frontier.append((ux, uy))
                break

    targets = frontier if frontier else list(un_set)
    if not targets:
        targets = [(ox, oy)]

    candidates = []
    for tx, ty in targets:
        candidates.append((max(0, min(w - 1, tx)), max(0, min(h - 1, ty))))

    move_opts = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_val = None

    # Deterministic preference order: sort targets to break ties consistently
    targets_sorted = sorted(set(candidates), key=lambda t: (abs(t[0] - sx) + abs(t[1] - sy), t[0], t[1]))

    # Evaluate moves by (1) best reachability toward frontier/unclaimed, (2) distance to opponent as secondary
    for dx, dy in move_opts:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        best_target_dist = 10**9
        # Move score: prioritize getting adjacent/onto cells that are adjacent to opponent territory (flipping)
        for tx, ty in targets_sorted[:12]:
            d = abs(tx - nx) + abs(ty - ny)
            if d < best_target_dist:
                best_target_dist = d
        # If standing on/next to opponent territory helps flipping, prefer it
        adj_opp = 0
        for ddx, ddy in neigh:
            if (nx + ddx, ny + ddy) in opp_set:
                adj_opp = 1
                break
        d_opp = abs(ox - nx) + abs(oy - ny)
        val = (0 if adj_opp else 1, best_target_dist, d_opp, nx, ny)
        if best_val is None or val < best_val:
            best_val = val
            best = (dx, dy)

    return list(best if best is not None else (0, 0))