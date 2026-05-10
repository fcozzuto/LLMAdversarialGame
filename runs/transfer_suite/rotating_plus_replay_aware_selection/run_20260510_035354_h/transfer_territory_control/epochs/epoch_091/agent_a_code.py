def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    ax, ay = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (ax, ay))
    obstacles = observation.get("obstacles") or []
    unclaimed = observation.get("unclaimed_cells") or []

    ob = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            ob.add((int(p[0]), int(p[1])))

    uc = []
    for p in unclaimed:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            uc.append((int(p[0]), int(p[1])))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    target = None
    if uc:
        bestd = 10**9
        for x, y in uc:
            d = abs(x - ax) + abs(y - ay)
            if d < bestd:
                bestd = d
                target = (x, y)

    def best_score(x, y):
        dx = abs(x - ox) + abs(y - oy)
        if target is None:
            return (0, -dx)  # prefer farther from opponent
        dt = abs(x - target[0]) + abs(y - target[1])
        return (dt, -dx)

    best = None
    best_key = None
    for mx, my in moves:
        nx, ny = ax + mx, ay + my
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in ob:
            continue
        k = best_score(nx, ny)
        if best_key is None or k < best_key:
            best_key = k
            best = [mx, my]
    if best is None:
        return [0, 0]
    return best