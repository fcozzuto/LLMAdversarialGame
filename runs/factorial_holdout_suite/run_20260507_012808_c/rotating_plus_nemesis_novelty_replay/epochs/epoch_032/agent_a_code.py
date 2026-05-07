def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x = int(r[0]); y = int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    dirs = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    moves = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            moves.append((dx, dy))

    if not moves:
        return [0, 0]

    if resources:
        best = None
        best_val = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            # Prefer being closer to our nearest resource; also prefer farther from opponent.
            # Add small deterministic tie-break using dx,dy.
            my_dist = min(man(nx, ny, rx, ry) for rx, ry in resources)
            opp_dist = min(man(ox, oy, rx, ry) for rx, ry in resources)
            val = (opp_dist - my_dist, my_dist, -(abs(dx) + abs(dy)), dx, dy)
            if best_val is None or val > best_val:
                best_val = val
                best = (dx, dy)
        return [int(best[0]), int(best[1])]

    # No resources: drift away from opponent while staying deterministic.
    best = None
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        val = (man(nx, ny, ox, oy), -(abs(dx) + abs(dy)), dx, dy)
        if best_val is None or val > best_val:
            best_val = val
            best = (dx, dy)
    return [int(best[0]), int(best[1])]