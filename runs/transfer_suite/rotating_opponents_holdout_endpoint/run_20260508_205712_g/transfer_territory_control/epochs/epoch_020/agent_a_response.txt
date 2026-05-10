def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    sx, sy = int(sx), int(sy)
    obstacles = set((int(x), int(y)) for x, y in (observation.get("obstacles", []) or []))
    selfT = set((int(x), int(y)) for x, y in (observation.get("self_territory", []) or []))
    oppT = set((int(x), int(y)) for x, y in (observation.get("opponent_territory", []) or []))
    unC = set((int(x), int(y)) for x, y in (observation.get("unclaimed_cells", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    neigh8 = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

    # Prefer contesting cells adjacent to opponent territory (intercept their edge expansion)
    cand = []
    if unC:
        for x, y in unC:
            for dx, dy in neigh8:
                nx, ny = x + dx, y + dy
                if (nx, ny) in oppT:
                    # tie-break deterministically by (x,y)
                    cand.append((x, y))
                    break

    if cand:
        # choose nearest candidate to current position (Manhattan)
        tx, ty = min(cand, key=lambda p: (abs(p[0] - sx) + abs(p[1] - sy), p[0], p[1]))
    elif unC:
        tx, ty = min(unC, key=lambda p: (abs(p[0] - sx) + abs(p[1] - sy), p[0], p[1]))
    elif oppT:
        tx, ty = min(oppT, key=lambda p: (abs(p[0] - sx) + abs(p[1] - sy), p[0], p[1]))
    else:
        return [0, 0]

    def cell_val(nx, ny):
        if not inb(nx, ny) or (nx, ny) in obstacles:
            return -10**12
        d = abs(nx - tx) + abs(ny - ty)
        # Moving toward target is primary
        val = -2.0 * d
        # If stepping into opponent territory, only do it if it moves us closer meaningfully
        if (nx, ny) in oppT:
            val += 3.5 - 1.5 * d
        # Prefer stepping into unclaimed to claim territory
        elif (nx, ny) in unC:
            val += 2.5 - 1.0 * d
        # Avoid stepping back into our own territory only slightly (still ok)
        if (nx, ny) in selfT:
            val += 0.2
        return val

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        v = cell_val(nx, ny)
        if v > best_val or (v == best_val and (dx, dy) < best_move):
            best_val = v
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]