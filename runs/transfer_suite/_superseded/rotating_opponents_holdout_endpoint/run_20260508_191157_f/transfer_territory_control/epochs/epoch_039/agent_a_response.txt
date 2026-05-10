def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocked = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    self_terr = set((int(p[0]), int(p[1])) for p in observation.get("self_territory") or [])
    opp_terr = set((int(p[0]), int(p[1])) for p in observation.get("opponent_territory") or [])
    unclaimed = set((int(p[0]), int(p[1])) for p in observation.get("unclaimed_cells") or [])

    neigh = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def adj_terr(x, y, terr):
        for dx, dy in neigh:
            if dx == 0 and dy == 0: 
                continue
            nx, ny = x + dx, y + dy
            if (nx, ny) in terr:
                return True
        return False
    def min_manh_to_unclaimed(x, y):
        best = 10**9
        for ux, uy in unclaimed:
            d = abs(ux - x) + abs(uy - y)
            if d < best:
                best = d
        return best if best < 10**9 else 0

    best_score = -10**18
    best = (0, 0)
    for dx, dy in neigh:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocked:
            continue

        if (nx, ny) in self_terr:
            base = 0
        elif (nx, ny) in opp_terr:
            base = 3  # flipping opponent territory
        elif (nx, ny) in unclaimed:
            base = 2  # taking new ground
        else:
            base = -1  # moving into unknown but non-claimable area (unlikely)

        # tactical pressure: move next to opponent territory to enable future flips
        press = 1 if adj_terr(nx, ny, opp_terr) else 0
        # consolidate: prefer expanding alongside our territory
        expand = 1 if adj_terr(nx, ny, self_terr) else 0

        # chase nearby unclaimed while staying away from opponent unless capturing
        dist_unc = min_manh_to_unclaimed(nx, ny)
        dist_opp = abs(nx - ox) + abs(ny - oy)
        score = base + 1.5 * press + 0.8 * expand - 0.03 * dist_unc + 0.01 * dist_opp

        # deterministic tie-break: lexicographic by (dx,dy)
        if score > best_score or (score == best_score and (dx, dy) < best):
            best_score = score
            best = (dx, dy)

    return [int(best[0]), int(best[1])]