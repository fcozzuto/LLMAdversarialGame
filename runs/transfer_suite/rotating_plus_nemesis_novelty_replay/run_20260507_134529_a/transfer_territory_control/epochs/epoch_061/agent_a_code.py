def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    self_terr = set((int(p[0]), int(p[1])) for p in (observation.get("self_territory") or []) if isinstance(p, (list, tuple)) and len(p) >= 2)
    opp_terr = set((int(p[0]), int(p[1])) for p in (observation.get("opponent_territory") or []) if isinstance(p, (list, tuple)) and len(p) >= 2)
    unclaimed = set((int(p[0]), int(p[1])) for p in (observation.get("unclaimed_cells") or []) if isinstance(p, (list, tuple)) and len(p) >= 2)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    neigh = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_sc = -10**18

    # Deterministic move evaluation: prioritize stealing opponent cells, then capturing unclaimed cells near opponent.
    for dx, dy in neigh:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        sc = 0.0
        if (nx, ny) in opp_terr:
            sc += 6.0
        if (nx, ny) in self_terr:
            sc -= 0.2
        if (nx, ny) in unclaimed:
            sc += 1.5

        # Boundary pressure: encourage stepping toward unclaimed adjacent to opponent territory; discourage giving opponent access.
        cnt_u_adj = 0
        cnt_opp_adj = 0
        cnt_self_adj = 0
        for ddx, ddy in neigh:
            ax, ay = nx + ddx, ny + ddy
            if not inb(ax, ay) or (ax, ay) in obstacles:
                continue
            if (ax, ay) in unclaimed:
                cnt_u_adj += 1
            if (ax, ay) in opp_terr:
                cnt_opp_adj += 1
            if (ax, ay) in self_terr:
                cnt_self_adj += 1

        sc += 0.35 * cnt_u_adj
        sc += 0.55 * cnt_opp_adj
        sc -= 0.15 * cnt_self_adj

        # Mild anti-crowd: avoid moving directly into opponent proximity unless stealing.
        dist = abs(nx - ox) + abs(ny - oy)
        sc -= 0.03 * dist
        if sc > best_sc or (sc == best_sc and (dx, dy) < best):
            best_sc = sc
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [best[0], best[1]]