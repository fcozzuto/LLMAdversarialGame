def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []

    obstacles = set()
    for p in obstacles_list:
        if p is not None and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def best_index(cands):
        if not cands:
            return (0, 0)
        best = cands[0][0]
        for v, m in cands[1:]:
            if v > best[0] or (v == best[0] and m < best[1]):
                best = (v, m)
        return best[1]

    if resources:
        best_moves = []
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            # Prefer closer to nearest resource; tie-break by going away from opponent.
            min_res = 10**9
            for r in resources:
                if r is None or len(r) < 2:
                    continue
                rx, ry = r[0], r[1]
                d = abs(nx - rx) + abs(ny - ry)
                if d < min_res:
                    min_res = d
            opp_d = abs(nx - ox) + abs(ny - oy)
            # Higher is better: negative distance to resource + small safety bonus.
            val = (-min_res, opp_d)
            best_moves.append((val, (dx, dy)))
        # Convert tuple compare to deterministic pick: compare by val[0] then val[1]
        best = None
        best_m = (0, 0)
        for v, m in best_moves:
            if best is None or v > best or (v == best and m < best_m):
                best = v
                best_m = m
        return [best_m[0], best_m[1]]

    # No resources: move toward center while avoiding opponent a bit.
    tx = (w - 1) // 2
    ty = (h - 1) // 2
    best_m = (0, 0)
    best_key = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        key = (-(abs(nx - tx) + abs(ny - ty)), abs(nx - ox) + abs(ny - oy), -dx, -dy)
        if best_key is None or key > best_key:
            best_key = key
            best_m = (dx, dy)
    return [best_m[0], best_m[1]]