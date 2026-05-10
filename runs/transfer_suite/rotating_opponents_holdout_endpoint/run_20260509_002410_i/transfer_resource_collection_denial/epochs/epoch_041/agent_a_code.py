def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y) and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def manh(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    deltas = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    # Step 1: build a priority target pool (prefer winning races).
    pool = []
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        # primary: race advantage; secondary: prefer closer (low myd); tertiary: prefer resources further from opponent in manhattan
        race = opd - myd
        pool.append((race, -myd, manh(ox, oy, rx, ry), rx, ry))
    pool.sort(reverse=True)

    # Choose best move by evaluating a 1-step look at top candidates.
    best_move = [0, 0]
    best_val = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy

        val = -10**18
        for i in range(min(6, len(pool))):
            _, _, _, rx, ry = pool[i]
            myd2 = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            # Emphasize ensuring we don't fall behind; slight bias toward reducing manhattan.
            race2 = opd - myd2
            manh2 = manh(nx, ny, rx, ry)
            v = race2 * 1000 - myd2 * 10 - manh2
            if v > val:
                val = v
        if val > best_val:
            best_val = val
            best_move = [nx - sx, ny - sy]

    return best_move