def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for b in observation.get("obstacles") or []:
        if b and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                obstacles.add((bx, by))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if resources:
        # Greedy: move that minimizes distance to nearest resource.
        best = None
        best_val = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            md = None
            for rx, ry in resources:
                d = abs(nx - rx) + abs(ny - ry)
                if md is None or d < md:
                    md = d
            if md is None:
                continue
            # Small tie-breaker: prefer moving away from opponent.
            val = (md, -(abs(nx - ox) + abs(ny - oy)))
            if best_val is None or val < best_val:
                best_val = val
                best = [dx, dy]
        if best is not None:
            return best

    # Fallback: deterministic move away from obstacles towards staying in bounds, else towards opponent.
    # Try to move to cell that maximizes distance from opponent (or minimizes if blocked).
    candidates = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny):
            dist_op = abs(nx - ox) + abs(ny - oy)
            candidates.append((dist_op, dx, dy))
    if candidates:
        candidates.sort(key=lambda t: (-t[0], t[1], t[2]))
        return [candidates[0][1], candidates[0][2]]

    # If completely surrounded, stay put.
    return [0, 0]