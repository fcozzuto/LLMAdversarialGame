def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    x, y = observation.get("self_position", (0, 0))
    selfT = set(tuple(p) for p in (observation.get("self_territory") or []) if p is not None and len(p) >= 2)
    oppT = set(tuple(p) for p in (observation.get("opponent_territory") or []) if p is not None and len(p) >= 2)
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []) if p is not None and len(p) >= 2)
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []) if p is not None and len(p) >= 2)

    deltas = [(-1, -1), (0, -1), (1, -1),
              (-1, 0),  (0, 0),  (1, 0),
              (-1, 1),  (0, 1),  (1, 1)]
    deltas.sort()

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    neigh_dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def frontier_score(px, py):
        # encourage expanding into nearby unclaimed and contesting opponent boundary
        fs = 0
        for dx, dy in neigh_dirs:
            nx, ny = px + dx, py + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                if (nx, ny) in unclaimed:
                    fs += 2
                elif (nx, ny) in oppT:
                    fs += 1
                elif (nx, ny) in selfT:
                    fs += 0
        return fs

    def dist_to_nearest_unclaimed(px, py, limit=3):
        # deterministic small-radius distance to keep direction
        best = 10**9
        for gx, gy in unclaimed:
            d = abs(gx - px) + abs(gy - py)
            if d < best:
                best = d
        if best > limit:
            return limit
        return best

    if not unclaimed and not oppT:
        return [0, 0]

    best_move = (0, 0)
    best_val = -10**18
    center_bias = -abs(x - (w - 1) / 2) - abs(y - (h - 1) / 2)

    for dx, dy in deltas:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        val = 0
        if (nx, ny) in unclaimed:
            val += 30
        elif (nx, ny) in oppT:
            val += 8
        elif (nx, ny) in selfT:
            val += 2

        val += frontier_score(nx, ny)

        # slight preference to progress toward nearest unclaimed to avoid looping
        d = dist_to_nearest_unclaimed(nx, ny, limit=6)
        val += (6 - d) * 1.2

        # mild center pressure
        val += 0.05 * ((-abs(nx - (w - 1) / 2) - abs(ny - (h - 1) / 2)) - center_bias)

        # keep deterministic tie-break: deltas order already sorted
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]