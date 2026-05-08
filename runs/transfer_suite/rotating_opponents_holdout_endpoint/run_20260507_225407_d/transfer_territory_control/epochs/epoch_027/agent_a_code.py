def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    sx, sy = int(sx), int(sy)

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    obs = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    opp_terr = set()
    for p in observation.get("opponent_territory") or []:
        if p and len(p) >= 2:
            opp_terr.add((int(p[0]), int(p[1])))

    unq = set()
    for p in observation.get("unclaimed_cells") or []:
        if p and len(p) >= 2:
            unq.add((int(p[0]), int(p[1])))

    def man(a, b): return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Immediate flip if possible
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obs and (nx, ny) in opp_terr:
            return [dx, dy]

    # Build frontier targets: unclaimed adjacent to opponent territory
    frontier = set()
    for ox, oy in opp_terr:
        for dx, dy in dirs:
            ax, ay = ox + dx, oy + dy
            if inb(ax, ay) and (ax, ay) not in obs and (ax, ay) in unq:
                frontier.add((ax, ay))

    # Fallback: any unclaimed, else stay
    candidates = list(frontier) if frontier else list(unq)
    if not candidates:
        return [0, 0]

    # Deterministic target choice: closest to frontier, then tie-break toward opponent cluster direction
    opp_pos = observation.get("opponent_position", [w - 1, h - 1])
    oxp, oyp = int(opp_pos[0]), int(opp_pos[1])
    target = None
    best = None
    for t in candidates:
        score = (man((sx, sy), t), man((oxp, oyp), t), t[0], t[1])
        if best is None or score < best:
            best = score
            target = t
    tx, ty = target

    # Choose move that minimizes distance to target and prefers entering unclaimed/near frontier
    best_move = [0, 0]
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        # Value components: main distance, bonus for unclaimed, slight bonus for proximity to opponent territory
        d = man((nx, ny), (tx, ty))
        val = d
        if (nx, ny) in unq:
            val -= 0.35
        if (nx, ny) in opp_terr:
            val -= 2.0
        # Encourage stepping onto cells adjacent to opponent territory (counterclaim pressure)
        near_opp = False
        for adx, ady in dirs:
            ax, ay = nx + adx, ny + ady
            if inb(ax, ay) and (ax, ay) in opp_terr:
                near_opp = True
                break
        if near_opp:
            val -= 0.15
        # Deterministic tie-break: lexicographic dx,dy order
        tie = (val, dx, dy)
        if best_val is None or tie < best_val:
            best_val = tie
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]