def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)

    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs_set = set()
    for o in obstacles:
        if isinstance(o, (list, tuple)) and len(o) == 2:
            obs_set.add((int(o[0]), int(o[1])))

    def inb(x, y):
        return 0 <= x < W and 0 <= y < H

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    cx0, cy0 = (W - 1) // 2, (H - 1) // 2

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_val = -10**18

    if resources:
        # Pre-sort resources deterministically by position for stable tie-breaking
        res_sorted = sorted((int(x), int(y)) for x, y in resources)
    else:
        res_sorted = []

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if (nx, ny) in obs_set or not inb(nx, ny):
            continue

        if not res_sorted:
            # Go to center while avoiding edges
            v = -man(nx, ny, cx0, cy0) - 0.001 * (man(nx, ny, 0, 0) + man(nx, ny, W - 1, H - 1))
        else:
            # Evaluate move by comparing how soon we can reach a resource vs opponent
            v = -10**18
            for rx, ry in res_sorted:
                sd = man(nx, ny, rx, ry)
                od = man(ox, oy, rx, ry)
                # Immediate capture dominates
                if sd == 0:
                    cand = 10**12 + (od == 1) * 10**6
                else:
                    # Prefer resources where we are closer (od - sd), then closer absolute
                    cand = (od - sd) * 1000 - sd
                    # Slightly prefer moves that also progress toward center to reduce dithering
                    cand -= 0.01 * man(nx, ny, cx0, cy0)
                # Small deterministic tie-break: favor lower resource coordinates
                cand -= 0.000001 * (rx + 17 * ry)
                if cand > v:
                    v = cand
            # Secondary tie-break: prefer decreasing distance to best resource we consider
            v -= 0.00001 * man(nx, ny, ox, oy)

        if v > best_val:
            best_val = v
            best_move = (dx, dy)
        elif v == best_val:
            # Deterministic tie-break by move order
            if (dx, dy) == (best_move[0], best_move[1]):
                continue
            # Keep smaller lexicographic move for stability
            if (dx, dy) < best_move:
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]