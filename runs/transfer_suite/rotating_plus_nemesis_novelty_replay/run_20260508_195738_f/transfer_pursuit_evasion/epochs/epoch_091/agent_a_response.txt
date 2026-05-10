def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def adj_block(x, y):
        c = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx or dy:
                    if (x + dx, y + dy) in obstacles:
                        c += 1
        return c

    best_move = [0, 0]
    best_val = -10**18
    for mdx, mdy in moves:
        nx, ny = sx + mdx, sy + mdy
        if not valid(nx, ny):
            continue

        # opponent best response: maximize distance from our new position
        worst_d = -1
        for odx, ody in moves:
            ex, ey = ox + odx, oy + ody
            if not valid(ex, ey):
                continue
            d = dist(nx, ny, ex, ey)
            if d > worst_d:
                worst_d = d

        # if all opponent moves invalid, worst_d stays -1 -> treat as current
        if worst_d < 0:
            worst_d = dist(nx, ny, ox, oy)

        # our objective: minimize worst-case distance; deterministic tie-break on obstacle clearance
        val = -worst_d - 0.05 * (adj_block(nx, ny))
        if val > best_val:
            best_val = val
            best_move = [mdx, mdy]

    # ensure deterministic valid return
    bx, by = sx + best_move[0], sy + best_move[1]
    if not valid(bx, by):
        return [0, 0]
    return best_move