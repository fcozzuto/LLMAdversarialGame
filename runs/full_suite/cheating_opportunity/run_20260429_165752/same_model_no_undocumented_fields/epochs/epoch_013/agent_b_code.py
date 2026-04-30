def choose_move(observation):
    x, y = observation.get("self_position", [0, 0]) or [0, 0]
    x, y = int(x), int(y)
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]
    ox, oy = int(ox), int(oy)

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs = set()
    for o in obstacles:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            ox2, oy2 = int(o[0]), int(o[1])
            if inb(ox2, oy2):
                obs.add((ox2, oy2))

    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if inb(rx, ry) and (rx, ry) not in obs:
                res.append((rx, ry))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def mindist(nx, ny):
        if not res:
            return 10**9
        best = 10**9
        for rx, ry in res:
            d = abs(nx - rx) + abs(ny - ry)
            if d < best:
                best = d
        return best

    def oppdist(nx, ny):
        return abs(nx - ox) + abs(ny - oy)

    best_move = (0, 0)
    best_key = None

    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        dres = mindist(nx, ny)
        dop = oppdist(nx, ny)
        key = (-dres, dop, dx, dy)  # maximize closeness to resources; then distance from opponent; then deterministic
        if best_key is None or key > best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]