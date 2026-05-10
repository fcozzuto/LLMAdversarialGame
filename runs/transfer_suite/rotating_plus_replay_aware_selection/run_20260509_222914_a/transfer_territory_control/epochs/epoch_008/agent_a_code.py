def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    targets = []
    rem = observation.get("remaining_resource_count")
    if rem is None:
        rem = len(observation.get("resources") or [])
    if (isinstance(rem, int) and rem > 0) or (observation.get("resources") is not None):
        for p in observation.get("resources") or []:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = p[0], p[1]
                if isinstance(x, int) and isinstance(y, int) and valid(x, y):
                    targets.append((x, y))

    if not targets:
        for p in observation.get("unclaimed_cells") or []:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = p[0], p[1]
                if isinstance(x, int) and isinstance(y, int) and valid(x, y):
                    targets.append((x, y))

    if not targets:
        targets = [(ox, oy)]

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    best = (10**9, 0)
    best_move = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d = min(dist((nx, ny), t) for t in targets)
        if d < best[0]:
            best = (d, 0)
            best_move = (dx, dy)
        elif d == best[0]:
            if moves.index((dx, dy)) < moves.index(best_move):
                best_move = (dx, dy)
    return [best_move[0], best_move[1]]