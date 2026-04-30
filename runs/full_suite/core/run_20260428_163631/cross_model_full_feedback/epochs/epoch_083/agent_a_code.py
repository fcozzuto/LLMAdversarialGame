def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in (observation.get("resources") or []):
        if r and len(r) >= 2:
            x = int(r[0]); y = int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    dxs = (-1, 0, 1)
    dys = (-1, 0, 1)

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    def mindist(x, y, pts):
        best = None
        for a, b in pts:
            d = abs(x - a) + abs(y - b)
            if best is None or d < best:
                best = d
        return 10**9 if best is None else best

    legal = []
    for dx in dxs:
        for dy in dys:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                legal.append((dx, dy))

    if not legal:
        return [0, 0]

    # If no resources, drift away from opponent deterministically.
    if not resources:
        best = None
        bestpair = None
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            score = abs(nx - ox) + abs(ny - oy)
            if best is None or score > best or (score == best and (dx, dy) < bestpair):
                best = score; bestpair = (dx, dy)
        return [bestpair[0], bestpair[1]]

    # Otherwise, go toward nearest resource while mildly avoiding the opponent.
    best = None
    bestpair = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        dres = mindist(nx, ny, resources)
        dop = abs(nx - ox) + abs(ny - oy)
        # Prefer smaller resource distance; break ties by larger opponent distance; then lexicographic.
        score = (-dres, dop)
        if best is None or score > best or (score == best and (dx, dy) < bestpair):
            best = score; bestpair = (dx, dy)
    return [bestpair[0], bestpair[1]]