def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    self_terr = set(tuple(t) for t in (observation.get("self_territory") or []))
    opp_terr = set(tuple(t) for t in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(t) for t in (observation.get("unclaimed_cells") or []))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    center = (w // 2, h // 2)
    targets = []
    if unclaimed:
        targets = list(unclaimed)
    elif opp_terr:
        targets = list(opp_terr)
    else:
        targets = [center]

    # Filter targets to keep evaluation cheap and focused
    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    filtered = []
    for (tx, ty) in targets:
        if in_bounds(tx, ty):
            d = abs(tx - sx) + abs(ty - sy)
            if d <= 10:
                filtered.append((tx, ty))
    if not filtered:
        filtered = targets

    best_move = (0, 0)
    best_v = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue

        d_to_opp = abs(nx - ox) + abs(ny - oy)
        d_to_center = abs(nx - center[0]) + abs(ny - center[1])

        cell_is_self = (nx, ny) in self_terr
        cell_is_opp = (nx, ny) in opp_terr
        cell_is_unclaimed = (nx, ny) in unclaimed

        # Goal: grab unclaimed / opponent nearby; if nothing, move toward center/front.
        local_best = 10**18
        for (tx, ty) in filtered:
            d = abs(nx - tx) + abs(ny - ty)
            if d < local_best:
                local_best = d

        v = 0.0
        v += (30.0 if cell_is_unclaimed else 0.0)
        v += (18.0 if cell_is_opp else 0.0)
        v += (8.0 if cell_is_self else 0.0)

        # Prefer moves that reduce distance to the best target
        v += -2.5 * local_best

        # Avoid drifting into opponent while countering
        v += -0.35 * d_to_opp

        # Slightly prefer center to expand territory
        v += -0.08 * d_to_center

        if (nx, ny) in opp_terr:
            # Entering opponent-owned cell flips control; be decisive
            v += 25.0

        # Deterministic tie-break: smallest dx, then smallest dy, then lexicographic
        if v > best_v + 1e-9:
            best_v = v
            best_move = (dx, dy)
        elif abs(v - best_v) <= 1e-9:
            cand = (dx, dy)
            if cand < best_move:
                best_move = cand

    return [int(best_move[0]), int(best_move[1])]