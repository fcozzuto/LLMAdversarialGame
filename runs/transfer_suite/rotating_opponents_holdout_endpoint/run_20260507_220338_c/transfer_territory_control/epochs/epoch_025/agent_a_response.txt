def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    sx, sy = int(sx), int(sy)

    obstacles = set((int(x), int(y)) for x, y in (observation.get("obstacles") or []))
    un = set((int(x), int(y)) for x, y in (observation.get("unclaimed_cells") or []))
    my = set((int(x), int(y)) for x, y in (observation.get("self_territory") or []))
    opp = set((int(x), int(y)) for x, y in (observation.get("opponent_territory") or []))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    tx, ty = None, None

    if un:
        tx, ty = min(un, key=lambda p: abs(p[0] - sx) + abs(p[1] - sy))
    else:
        # Pressure: pick a cell adjacent (8-neigh) to opponent territory that is either unclaimed or own territory
        adj = set()
        for x, y in opp:
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    if dx == 0 and dy == 0:
                        continue
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < w and 0 <= ny < h:
                        if (nx, ny) in un or (nx, ny) in my or (nx, ny) not in opp:
                            adj.add((nx, ny))
        if adj:
            tx, ty = min(adj, key=lambda p: abs(p[0] - sx) + abs(p[1] - sy))

    if tx is None:
        return [0, 0]

    best_val = -10**18
    best_move = (0, 0)
    man = abs(tx - sx) + abs(ty - sy)

    def cell_val(nx, ny):
        d = abs(tx - nx) + abs(ty - ny)
        if (nx, ny) in obstacles:
            return -10**15
        v = 0
        if (nx, ny) in un:
            v += 1000 - 3 * d
        if (nx, ny) in my:
            v += 20 - d
        if (nx, ny) in opp:
            v += 80 - 2 * d  # flipping on entry
        # Prefer moves that reduce distance to the target
        v += (man - d) * 10
        # Keep away from obstacles slightly
        for ox, oy in obstacles:
            if abs(ox - nx) <= 1 and abs(oy - ny) <= 1 and not (ox == nx and oy == ny):
                v -= 8
                break
        return v

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            v = cell_val(nx, ny)
            if v > best_val or (v == best_val and (dx, dy) < best_move):
                best_val = v
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]