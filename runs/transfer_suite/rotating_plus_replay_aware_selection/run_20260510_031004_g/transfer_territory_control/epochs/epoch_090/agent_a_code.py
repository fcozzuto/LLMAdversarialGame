def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    px, py = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    obstacles = set(map(tuple, observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def blocked(x, y):
        return (x, y) in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    unclaimed = observation.get("unclaimed_cells", []) or []
    resources = observation.get("resources", []) or []
    candidates = []
    for cell in unclaimed:
        if isinstance(cell, (list, tuple)) and len(cell) == 2:
            x, y = cell
            if inb(x, y) and not blocked(x, y):
                candidates.append((x, y))
    if not candidates:
        for r in resources:
            if isinstance(r, (list, tuple)) and len(r) == 2:
                x, y = r
                if inb(x, y) and not blocked(x, y):
                    candidates.append((x, y))
    if candidates:
        tx, ty = min(candidates, key=lambda c: abs(c[0] - sx) + abs(c[1] - sy))
    else:
        tx, ty = px, py

    best = None
    bestd = 10**9
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or blocked(nx, ny):
            continue
        d = abs(nx - tx) + abs(ny - ty)
        do = abs(nx - px) + abs(ny - py)
        score = d * 2 + do * 0 - (0 if (nx, ny) == (tx, ty) else 0)
        if score < bestd:
            bestd = score
            best = [dx, dy]
    if best is None:
        return [0, 0]
    return best