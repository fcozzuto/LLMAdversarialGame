def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    unclaimed = []
    for p in observation.get("unclaimed_cells") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            unclaimed.append((int(p[0]), int(p[1])))

    opp_terr = []
    for p in observation.get("opponent_territory") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            opp_terr.append((int(p[0]), int(p[1])))

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    neigh = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inside(nx, ny) and (nx, ny) not in obstacles:
            neigh.append((nx, ny, dx, dy))

    # Target selection: contest useful unclaimed near center; otherwise shadow/interrupt opponent territory.
    targets = unclaimed if unclaimed else opp_terr
    if targets:
        best = None
        for tx, ty in targets:
            ds = abs(tx - sx) + abs(ty - sy)
            do = abs(tx - ox) + abs(ty - oy)
            dc = abs(tx - cx) + abs(ty - cy)
            # Prefer cells we can reach earlier; also prefer center control.
            sc = (ds - 0.65 * do) + 0.02 * dc
            if best is None or sc < best[0]:
                best = (sc, tx, ty)
        _, tx, ty = best
    else:
        tx, ty = int(round(cx)), int(round(cy))

    # Choose move that reduces distance to target; small bias toward center.
    bestm = (10**9, 0, 0)
    for nx, ny, dx, dy in neigh:
        d = abs(tx - nx) + abs(ty - ny)
        bias = 0.005 * (abs(nx - cx) + abs(ny - cy))
        score = d + bias
        if score < bestm[0]:
            bestm = (score, dx, dy)

    return [int(bestm[1]), int(bestm[2])]