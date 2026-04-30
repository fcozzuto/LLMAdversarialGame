def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    obst = set()
    for p in observation.get("obstacles", []) or []:
        try:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obst.add((x, y))
        except:
            pass

    resources = []
    for r in observation.get("resources", []) or []:
        try:
            x, y = int(r[0]), int(r[1])
            if inb(x, y) and (x, y) not in obst:
                resources.append((x, y))
        except:
            pass

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    legal = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obst:
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    def man(a, b):
        return abs(a[0]-b[0]) + abs(a[1]-b[1])

    # Target closest resource if available, else approach opponent to apply pressure
    if resources:
        best = None
        bestd = 10**9
        for rx, ry in resources:
            d = man((sx, sy), (rx, ry))
            if d < bestd:
                bestd = d
                best = (rx, ry)
        if best is not None:
            # move toward chosen resource if possible
            tx, ty = best
            best_move = None
            bestd2 = 10**9
            for dx, dy in legal:
                nx, ny = sx + dx, sy + dy
                d2 = abs(nx - tx) + abs(ny - ty)
                if d2 < bestd2:
                    bestd2 = d2
                    best_move = (dx, dy)
            if best_move is not None:
                return [best_move[0], best_move[1]]

    # If no resources or not moving toward resource, deterministic defensive/central strategy
    # Prefer staying or moving to reduce opponent proximity while staying within bounds and avoiding obstacles
    best_move = (0, 0)
    best_score = -10**9
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        # score: prefer positions closer to center and not adjacent to opponent if possible
        center_dx = abs(nx - w//2)
        center_dy = abs(ny - h//2)
        dist_opp = abs(nx - ox) + abs(ny - oy)
        score = -(center_dx + center_dy) * 2 - dist_opp
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]