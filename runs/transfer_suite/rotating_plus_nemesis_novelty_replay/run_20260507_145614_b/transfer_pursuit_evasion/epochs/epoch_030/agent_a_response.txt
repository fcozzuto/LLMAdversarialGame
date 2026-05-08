def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obst = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obst.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    role = (observation.get("self_role") or "").lower()
    evader = ("evader" in role) or ("escape" in role) or ("runner" in role) or ("flee" in role) or ("evade" in role)

    def neighbor_count(x, y):
        c = 0
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if inb(nx, ny):
                c += 1
        return c

    best_move = (0, 0)
    best_score = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        dist = abs(nx - ox) + abs(ny - oy)
        ncount = neighbor_count(nx, ny)

        # Score: pursuer minimizes distance; evader maximizes distance.
        # Add obstacle-awareness: prefer positions with more mobility.
        if evader:
            score = (dist * 10 + ncount)  # maximize
        else:
            score = (-dist * 10 + ncount)  # maximize (more is better)

        # Deterministic tie-break: prefer (0,0), then lexicographically smaller dx,dy
        tb = (0, 0) if (dx == 0 and dy == 0) else (dx + 2, dy + 2)
        key = (score, -tb[0], -tb[1])

        if best_score is None:
            best_score = key
            best_move = (dx, dy)
        else:
            if key > best_score:
                best_score = key
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]