def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    resources = list(observation.get("resources", []) or [])
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    cands = []
    for dx, dy in moves:
        nx, ny = int(sx + dx), int(sy + dy)
        if valid(nx, ny):
            cands.append((dx, dy, nx, ny))
    if not cands:
        return [0, 0]

    if resources:
        best = None
        for dx, dy, nx, ny in cands:
            nearest = min(resources, key=lambda r: (abs(nx - r[0]) + abs(ny - r[1]), r[0], r[1]))
            d = abs(nx - nearest[0]) + abs(ny - nearest[1])
            t = (d, abs(nx - ox) + abs(ny - oy), nx, ny, dx, dy)
            if best is None or t < best[0]:
                best = (t, dx, dy)
        return [best[1], best[2]]
    else:
        best = None
        for dx, dy, nx, ny in cands:
            d = abs(nx - ox) + abs(ny - oy)
            t = (d, nx, ny, dx, dy)
            if best is None or t < best[0]:
                best = (t, dx, dy)
        return [best[1], best[2]]