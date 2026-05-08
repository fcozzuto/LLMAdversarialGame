def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (w - 1, h - 1)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def norm_pos(p):
        if isinstance(p, (list, tuple)) and len(p) == 2:
            return int(p[0]), int(p[1])
        return None

    obstacles = set()
    for p in observation.get("obstacles") or []:
        q = norm_pos(p)
        if q is not None:
            obstacles.add(q)

    in_bounds = lambda x, y: 0 <= x < w and 0 <= y < h
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    unclaimed = [norm_pos(p) for p in (observation.get("unclaimed_cells") or [])]
    unclaimed = [p for p in unclaimed if p is not None and p not in obstacles]

    myT = set((norm_pos(p) for p in (observation.get("self_territory") or [])))
    myT.discard(None)
    oppT = set((norm_pos(p) for p in (observation.get("opponent_territory") or [])))
    oppT.discard(None)

    targets = unclaimed
    if not targets:
        targets = [p for p in oppT if p not in obstacles]

    if not targets:
        return [0, 0]

    unblocked_neighbors = 0
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if in_bounds(nx, ny) and (nx, ny) not in obstacles:
            unblocked_neighbors += 1

    # Prefer reaching nearest unclaimed; if tie, prefer cells more central vs opponent (territory_center_claim).
    opp_center_bias = 0
    for t in targets[: min(25, len(targets))]:
        if t in oppT:
            opp_center_bias += 1

    best = (None, -10**18)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue

        # How many options after moving (avoid getting stuck near obstacles).
        next_opts = 0
        for ddx, ddy in moves:
            tx, ty = nx + ddx, ny + ddy
            if in_bounds(tx, ty) and (tx, ty) not in obstacles:
                next_opts += 1

        # Choose best immediate objective: nearest target, but only sample deterministically.
        best_td = 10**9
        target_on_step = (nx, ny) in unclaimed or (nx, ny) in oppT
        sample = targets[: min(30, len(targets))]
        for t in sample:
            d = abs(nx - t[0]) + abs(ny - t[1])
            if d < best_td:
                best_td = d

        dist_to_opp = abs(nx - ox) + abs(ny - oy)
        # If stepping into opponent territory, it's valuable (flipping on entry).
        flip_bonus = 0.0
        if (nx, ny) in oppT:
            flip_bonus = 2.5
        # Encourage moving toward higher-quality points: nearer to targets, more room, and slightly away from opponent if unclaimed dominates.
        unclaimed_dom = 1.0 if unclaimed else 0.0
        v = (-best_td) + 0.15 * next_opts + 0.05 * dist_to_opp * (0.6 - unclaimed_dom) + flip_bonus
        # Deterministic tie-break: prefer lower x then lower y
        key = (nx, ny)
        if best[0] is None or v > best[1] or (v == best[1] and key < best[0]):
            best = (key, v)

    (tx, ty), _ = best
    return [tx - sx, ty - sy]