def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(0, 0), (1, 0), (0, 1), (-1, 0), (0, -1),
             (1, 1), (1, -1), (-1, 1), (-1, -1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def md(a, b): return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def closest_dist(pt, arr):
        if not arr:
            return 999
        best = 999
        for q in arr:
            d = md(pt, q)
            if d < best:
                best = d
        return best

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            score = -10**12
        else:
            # Target pressure: approach nearest resource
            dres = closest_dist((nx, ny), resources)
            # Opponent pressure: avoid being too close; if far, still bias slightly toward resources
            dop = md((nx, ny), (ox, oy))
            # Obstacle clearance: prefer cells with more space around
            dobs = closest_dist((nx, ny), list(obstacles)) if obstacles else 999
            # Deterministic composite score with tie-break by position later
            score = (-2.4 * dres) + (0.35 * dop) + (0.18 * dobs) - (0.02 * (dx * dx + dy * dy))

        # Tie-break deterministically by resulting position
        if score > best_score or (score == best_score and (nx, ny) < (sx + best_move[0], sy + best_move[1])):
            best_score = score
            best_move = (dx, dy)

    dx, dy = best_move
    return [int(dx), int(dy)]