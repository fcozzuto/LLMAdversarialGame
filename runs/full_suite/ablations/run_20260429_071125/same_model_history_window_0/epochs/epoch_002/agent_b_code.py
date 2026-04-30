def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # If no resources, drift toward opponent while avoiding obstacles
    if not resources:
        target = (ox, oy)
    else:
        # Choose resource to contest: prefer close to self and far from opponent
        best = None
        bestv = None
        for r in resources:
            dS = dist((sx, sy), r)
            dO = dist((ox, oy), r)
            v = dS - 0.9 * dO  # lower is better
            if best is None or v < bestv or (v == bestv and (r[0], r[1]) < (best[0], best[1])):
                best = r
                bestv = v
        target = best

    moves = [(0, 0), (-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # If target is current position, move toward next-best by forcing a move (still might be prevented)
    best_move = (0, 0)
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        dT = dist((nx, ny), target)
        dO = dist((nx, ny), (ox, oy))
        # Prefer being closer to target and slightly farther from opponent to avoid being crowded
        val = -dT + 0.06 * dO

        if best_val is None or val > best_val or (val == best_val and moves.index((dx, dy)) < moves.index(best_move)):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]