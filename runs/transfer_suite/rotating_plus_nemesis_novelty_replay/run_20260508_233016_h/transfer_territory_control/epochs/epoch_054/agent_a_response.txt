def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    ox, oy = observation.get("opponent_position", (sx, sy))

    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    inb = lambda x, y: 0 <= x < w and 0 <= y < h
    man = lambda ax, ay, bx, by: abs(ax - bx) + abs(ay - by)

    self_t = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_t = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = [tuple(p) for p in (observation.get("unclaimed_cells") or [])]

    edge_targets = []
    if unclaimed:
        for x, y in unclaimed:
            if x == 0 or x == w - 1 or y == 0 or y == h - 1:
                edge_targets.append((x, y))
    if not edge_targets:
        edge_targets = unclaimed if unclaimed else []

    if not edge_targets:
        cand = [(0, 0), (-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
        best = (0, 0)
        best_sc = -10**18
        for dx, dy in cand:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            sc = -man(nx, ny, w - 1, h - 1) if (sx + sy) < (w + h - 2) else -man(nx, ny, 0, 0)
            if sc > best_sc:
                best_sc, best = sc, (dx, dy)
        return [best[0], best[1]]

    candidates = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = (0, 0)
    best_sc = -10**18

    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        base = 0
        if (nx, ny) in opp_t:
            base += 5000
        elif (nx, ny) in unclaimed:
            base += 2000
        elif (nx, ny) in self_t:
            base += 400

        best_edge = 10**9
        far_from_opp = -10**9
        for tx, ty in edge_targets[:30]:
            d1 = man(nx, ny, tx, ty)
            if d1 < best_edge:
                best_edge = d1
            d2 = man(ox, oy, tx, ty)
            if d2 - d1 > far_from_opp:
                far_from_opp = d2 - d1

        sc = base + (-best_edge * 120) + (far_from_opp * 80)
        if sc > best_sc or (sc == best_sc and (dx, dy) < best):
            best_sc, best = sc, (dx, dy)

    return [int(best[0]), int(best[1])]