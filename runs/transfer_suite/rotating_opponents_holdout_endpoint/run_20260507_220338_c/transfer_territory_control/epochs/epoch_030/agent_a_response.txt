def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    sx, sy = int(sx), int(sy)
    ox, oy = observation.get("opponent_position") or (sx, sy)
    ox, oy = int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        obstacles.add((int(p[0]), int(p[1])))

    myset = set()
    for p in observation.get("self_territory") or []:
        myset.add((int(p[0]), int(p[1])))

    unclaimed = set()
    for p in observation.get("unclaimed_cells") or []:
        unclaimed.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    # Frontier: unclaimed adjacent to our territory, else any unclaimed
    frontier = []
    base = myset if myset else {(sx, sy)}
    for x, y in base:
        for dx, dy in ((-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)):
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and (nx, ny) in unclaimed:
                frontier.append((nx, ny))
    if not frontier:
        frontier = list(unclaimed)
    if not frontier:
        return [0, 0]

    # Prefer frontier cells that are closer to opponent (to pressure center leader archetype)
    # and tie-break deterministically by (y,x)
    tx, ty = min(frontier, key=lambda c: (max(abs(c[0]-ox), abs(c[1]-oy)), c[1], c[0]))

    # Choose best adjacent step (including diagonals and staying still)
    moves = [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1),(0,0)]
    best = (10**9, 10**9, None)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        d = max(abs(nx - tx), abs(ny - ty))  # Chebyshev
        # If already in our territory, slight bias to expand outward by moving toward frontier target
        bias = 0
        if (nx, ny) in myset:
            bias += 0.3
        # If moving into unclaimed, slight preference
        if (nx, ny) in unclaimed:
            bias -= 0.2
        # Deterministic tie-break
        key = (int(d*10 + bias*10), 0, dx, dy)
        if key < best[:2] + best[2:3] if best[2] is not None else True:
            best = (key[0], key[1], (dx, dy))
    if best[2] is None:
        return [0, 0]
    return [best[2][0], best[2][1]]