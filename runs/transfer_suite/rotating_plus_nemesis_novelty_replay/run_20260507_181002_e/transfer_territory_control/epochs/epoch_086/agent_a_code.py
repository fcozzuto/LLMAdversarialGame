def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def toset(v):
        s = set()
        for p in v or []:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                s.add((x, y))
        return s

    selfT = toset(observation.get("self_territory"))
    oppT = toset(observation.get("opponent_territory"))
    unclaimed = toset(observation.get("unclaimed_cells"))
    obstacles = toset(observation.get("obstacles"))
    resources = toset(observation.get("resources"))
    if not unclaimed and resources:
        unclaimed = set(resources)

    moves = [(0, 0), (1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    best = None
    best_val = -10**9

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(x, y, a, b):
        dx = x - a
        dy = y - b
        return (dx * dx + dy * dy)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            val = -10**6  # discourage invalid/blocked moves
        else:
            val = 0
            if (nx, ny) in selfT:
                val += 0.4
            elif (nx, ny) in unclaimed:
                val += 1.7
            elif (nx, ny) in oppT:
                val += 3.4  # flipping on entry is enabled
            else:
                val += 0.1  # rare: empty but not listed; slight preference

            # Expand away from opponent while still making progress
            d_opp = dist(nx, ny, ox, oy)
            val += 0.001 * d_opp

            # If there exist unclaimed cells, bias toward the closest one (avoid long detours)
            if unclaimed:
                md = None
                for (ux, uy) in unclaimed:
                    dd = dist(nx, ny, ux, uy)
                    if md is None or dd < md:
                        md = dd
                val += -0.0008 * md

        if val > best_val:
            best_val = val
            best = (dx, dy)

    return [int(best[0]), int(best[1])]