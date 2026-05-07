def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    # Deterministic tie-breaking order as listed
    best_move = (0, 0)
    best_score = (-10**9, -10**9)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        # Choose the resource we would contest best from the next position
        best_gap = -10**9
        best_selfd = 10**9
        for rx, ry in resources:
            selfd = cheb(nx, ny, rx, ry)
            oppd = cheb(ox, oy, rx, ry)
            gap = oppd - selfd  # positive means we're closer than opponent
            # Lexicographic: maximize gap, then minimize our distance (fastest collection)
            if gap > best_gap or (gap == best_gap and selfd < best_selfd):
                best_gap = gap
                best_selfd = selfd

        # Also add a small bias for reducing our own closest distance overall
        closest_self = min(cheb(nx, ny, rx, ry) for rx, ry in resources)
        score = (best_gap, -best_selfd - 0.01 * closest_self)
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]