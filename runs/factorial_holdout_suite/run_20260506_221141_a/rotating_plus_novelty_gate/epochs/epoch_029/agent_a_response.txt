def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    if not resources:
        return [0, 0]

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Pick best resource by who can arrive first (opponent earlier is bad).
    best = None
    best_key = None
    for p in resources:
        tx, ty = int(p[0]), int(p[1])
        if not inb(tx, ty) or (tx, ty) in obs:
            continue
        ds = md(sx, sy, tx, ty)
        do = md(ox, oy, tx, ty)
        key = ((do - ds), -(ds), -((tx + ty) & 1), -tx, -ty)
        if best_key is None or key > best_key:
            best_key = key
            best = (tx, ty)

    if best is None:
        return [0, 0]
    tx, ty = best

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    bestm = (0, 0)
    bestv = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        # Prefer closer to target; if equal, prefer cells where we stay ahead vs opponent.
        ds2 = md(nx, ny, tx, ty)
        do2 = md(ox, oy, tx, ty)
        key = (-(ds2), (do2 - ds2), -((nx + ny) & 1), -nx, -ny)
        if bestv is None or key > bestv:
            bestv = key
            bestm = (dx, dy)

    # If all moves blocked, stay.
    return [int(bestm[0]), int(bestm[1])]