def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) == 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def obs_pen(x, y):
        pen = 0.0
        for ax, ay in obstacles:
            d = cheb(x, y, ax, ay)
            if d == 0:
                pen += 50.0
            elif d == 1:
                pen += 2.0
            elif d == 2:
                pen += 0.6
        return pen

    # Deteministic pick: evaluate each legal delta by best "competitive value" over resources.
    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    best = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        # Competitive: prefer resources where we are closer than opponent; also avoid over-committing.
        best_val = None
        for rx, ry in resources:
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            # "Value" favors winning access now (od - sd), penalizes travel time, and lightly discourages going near obstacles.
            val = (od - sd) * 10.0 - sd - obs_pen(nx, ny)
            # If tied, prefer closer to the resource and lexicographically smaller coords for determinism.
            tie = (-sd, -rx, -ry)
            key = (val, tie)
            if best_val is None or key > best_val:
                best_val = key
        # Add a small opponent-avoid term to change behavior vs previous epochs: don't move into their chase region.
        opp = cheb(nx, ny, ox, oy)
        cur_score = best_val[0] - 0.08 * opp

        if best is None or cur_score > best[0] or (cur_score == best[0] and (dx, dy) < best[1]):
            best = (cur_score, (dx, dy))

    if best is None:
        # Fallback: stay or best adjacent without relying on obstacle-free checks
        return [0, 0]
    return [int(best[1][0]), int(best[1][1])]