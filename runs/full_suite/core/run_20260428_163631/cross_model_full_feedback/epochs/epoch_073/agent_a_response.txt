def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if inb(x, y) and (x, y) not in obstacles:
                resources.append((x, y))

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    legal = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    if not resources:
        # Expand away from opponent while staying near center-ish
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = None
        for dx, dy, nx, ny in legal:
            # maximize distance from opponent, break ties by minimizing distance to center
            key = (-manh(nx, ny, ox, oy), manh(nx, ny, tx, ty), nx, ny)
            if best is None or key < best[0]:
                best = (key, dx, dy)
        return [best[1], best[2]]

    # Choose resource where we are relatively closer than opponent (deterministic tie-break)
    best_r = None
    best_key = None
    for rx, ry in resources:
        ds = manh(sx, sy, rx, ry)
        do = manh(ox, oy, rx, ry)
        # Prefer winning the race: maximize (do - ds)
        key = (-(do - ds), ds, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_r = (rx, ry)

    rx, ry = best_r

    # Move to reduce our distance to target, but also keep opponent farther
    best = None
    for dx, dy, nx, ny in legal:
        dself = manh(nx, ny, rx, ry)
        dopp = manh(nx, ny, ox, oy)
        # primary: smaller dself; secondary: larger opponent distance; tertiary: deterministic
        key = (dself, -dopp, nx, ny)
        if best is None or key < best[0]:
            best = (key, dx, dy)
    return [best[1], best[2]]