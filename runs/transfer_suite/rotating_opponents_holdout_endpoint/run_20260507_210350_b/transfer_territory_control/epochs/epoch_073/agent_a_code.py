def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = map(int, observation.get("self_position") or (0, 0))
    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
    selfT = set((int(p[0]), int(p[1])) for p in (observation.get("self_territory") or []) if p and len(p) >= 2)
    oppT = set((int(p[0]), int(p[1])) for p in (observation.get("opponent_territory") or []) if p and len(p) >= 2)
    unclaimed = set((int(p[0]), int(p[1])) for p in (observation.get("unclaimed_cells") or []) if p and len(p) >= 2)

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1), (0, 0)]
    ox, oy = (w - 1) / 2.0, (h - 1) / 2.0

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def best_neighbor_unclaimed(x, y):
        bd = 10**9
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if (nx, ny) in unclaimed:
                d = abs(nx - x) + abs(ny - y)
                if d < bd:
                    bd = d
        return bd if bd != 10**9 else None

    best_mv = (0, 0)
    best_sc = -10**9
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        sc = 0
        if (nx, ny) in selfT:
            sc -= 0.2
        elif (nx, ny) in unclaimed:
            sc += 6
            dcen = abs(nx - ox) + abs(ny - oy)
            sc += max(0, 3 - 0.2 * dcen)
            nb = best_neighbor_unclaimed(nx, ny)
            if nb is not None:
                sc += 2.5 / (1 + nb)
        elif (nx, ny) in oppT:
            sc -= 2
            nb = best_neighbor_unclaimed(nx, ny)
            if nb is not None:
                sc += 3.5 / (1 + nb)
            # discourage stepping onto opponent territory unless it helps frontier
            dcen = abs(nx - ox) + abs(ny - oy)
            sc += max(0, 1 - 0.08 * dcen)
        else:
            # plain move to empty should only be used if it approaches unclaimed/center
            sc -= 0.4
            d = None
            if unclaimed:
                # deterministic: choose closest unclaimed by tie-breaking
                best = None
                for ux, uy in sorted(unclaimed):
                    dd = abs(ux - nx) + abs(uy - ny)
                    if best is None or dd < best[0]:
                        best = (dd, ux, uy)
                d = best[0]
                sc += max(0, 4 - 0.5 * d)
            sc += max(0, 2 - 0.2 * (abs(nx - ox) + abs(ny - oy)))

        if sc > best_sc:
            best_sc = sc
            best_mv = (dx, dy)
    return [int(best_mv[0]), int(best_mv[1])]