def choose_move(observation):
    w = observation.get("grid_width", 0)
    h = observation.get("grid_height", 0)
    if not isinstance(w, int) or not isinstance(h, int) or w <= 0 or h <= 0:
        return [0, 0]

    sx, sy = observation.get("self_position", (0, 0))
    obstacles = observation.get("obstacles") or []
    obs = {(x, y) for x, y in obstacles if isinstance(x, int) and isinstance(y, int)}
    self_terr = {(x, y) for x, y in (observation.get("self_territory") or []) if isinstance(x, int) and isinstance(y, int)}
    opp_terr = {(x, y) for x, y in (observation.get("opponent_territory") or []) if isinstance(x, int) and isinstance(y, int)}
    unclaimed = {(x, y) for x, y in (observation.get("unclaimed_cells") or []) if isinstance(x, int) and isinstance(y, int)}
    opp_pos = observation.get("opponent_position", (w - 1, h - 1))
    ox, oy = opp_pos if isinstance(opp_pos, (list, tuple)) and len(opp_pos) == 2 else (w - 1, h - 1)

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    neigh4 = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    frontier = []
    if self_terr:
        for ux, uy in unclaimed:
            for dx, dy in neigh4:
                if (ux + dx, uy + dy) in self_terr:
                    frontier.append((ux, uy))
                    break

    targets = frontier if frontier else list(unclaimed) if unclaimed else []
    if not targets:
        return [0, 0]

    best_t = None
    best_key = None
    for tx, ty in targets:
        d = (tx - sx) * (tx - sx) + (ty - sy) * (ty - sy)
        # slight bias toward pushing overall toward opponent side
        bias = (tx - ox) * (tx - ox) + (ty - oy) * (ty - oy)
        key = (d + 0.05 * bias, abs(tx - ox) + abs(ty - oy), tx, ty)
        if best_key is None or key < best_key:
            best_key, best_t = key, (tx, ty)

    tx, ty = best_t
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_m = None
    best_sc = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obs:
            continue
        if (nx, ny) in self_terr:
            sc = 1
        elif (nx, ny) in unclaimed:
            sc = 5
        elif (nx, ny) in opp_terr:
            sc = 3
        else:
            sc = 0
        dist = abs(tx - nx) + abs(ty - ny)
        sc += -0.35 * dist
        # deterministic tie-break
        key = (sc, -dx, -dy, nx, ny)
        if best_sc is None or key > best_sc:
            best_sc, best_m = key, (dx, dy)

    if best_m is None:
        return [0, 0]
    return [int(best_m[0]), int(best_m[1])]