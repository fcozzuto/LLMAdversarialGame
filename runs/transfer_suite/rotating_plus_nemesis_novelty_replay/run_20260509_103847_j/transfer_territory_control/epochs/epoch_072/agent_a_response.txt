def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    sx, sy = int(sx), int(sy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    selfT = set()
    for p in observation.get("self_territory") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            selfT.add((int(p[0]), int(p[1])))

    opT = set()
    for p in observation.get("opponent_territory") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            opT.add((int(p[0]), int(p[1])))

    unT = set()
    for p in observation.get("unclaimed_cells") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                unT.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def adj_count(x, y, S):
        c = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (x + dx, y + dy) in S:
                    c += 1
        return c

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    best = None
    best_sc = -10**18
    # Tie-break deterministically: prefer moves with smaller dx, then smaller dy
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        s = 0
        a_self = adj_count(nx, ny, selfT)
        a_op = adj_count(nx, ny, opT)

        if (nx, ny) in unT:
            s += 6 + 2 * a_self
        elif (nx, ny) in opT:
            s += 5 + 2 * a_self + 1 * a_op  # flipping on entry
        elif (nx, ny) in selfT:
            s += 1 + 2 * a_self
        else:
            s += 1 + a_self

        # Center pressure (opponent tends to center-claim)
        dist_now = abs(sx - cx) + abs(sy - cy)
        dist_next = abs(nx - cx) + abs(ny - cy)
        s += (dist_now - dist_next) * 1.5

        # If we can approach opponent territory, prioritize it locally
        if a_op > 0:
            s += 3 + a_op

        if s > best_sc or (s == best_sc and (best is None or (dx, dy) < best)):
            best_sc = s
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]