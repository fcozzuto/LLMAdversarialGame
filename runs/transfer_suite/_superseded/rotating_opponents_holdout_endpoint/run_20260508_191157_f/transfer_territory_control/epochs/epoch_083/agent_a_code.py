def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    sx, sy = int(sx), int(sy)
    ox, oy = observation.get("opponent_position") or [w - 1, h - 1]
    ox, oy = int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    selfT = set(tuple(p) for p in (observation.get("self_territory") or []))
    oppT = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def utility(x, y):
        if (x, y) in obstacles:
            return -10**9
        is_un = 1.0 if (x, y) in unclaimed else 0.0
        is_opp = 1.0 if (x, y) in oppT else 0.0
        is_self = 1.0 if (x, y) in selfT else 0.0
        adj_un = 0
        adj_opp = 0
        adj_self = 0
        for dx, dy in ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)):
            nx, ny = x + dx, y + dy
            if not inb(nx, ny):
                continue
            if (nx, ny) in unclaimed:
                adj_un += 1
            elif (nx, ny) in oppT:
                adj_opp += 1
            elif (nx, ny) in selfT:
                adj_self += 1
        dist = abs(x - ox) + abs(y - oy)
        # Strongly prefer capturing unclaimed; attacking opponent directly on entry (flip on entry).
        return (7.0 * is_un + 10.0 * is_opp + 1.0 * is_self) + (2.0 * adj_un) - (2.5 * adj_opp) + (0.5 * adj_self) - (0.05 * dist)

    best = [0, 0]
    best_u = -10**18
    # Deterministic tie-break: prefer dx,dy order as listed in dirs.
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        u = utility(nx, ny)
        if u > best_u:
            best_u = u
            best = [dx, dy]

    if best_u == -10**18:
        return [0, 0]
    return best