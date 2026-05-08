def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    self_terr = set()
    for p in (observation.get("self_territory") or []):
        if p and len(p) >= 2:
            self_terr.add((int(p[0]), int(p[1])))

    opp_terr = set()
    for p in (observation.get("opponent_territory") or []):
        if p and len(p) >= 2:
            opp_terr.add((int(p[0]), int(p[1])))

    unclaimed = set()
    for p in (observation.get("unclaimed_cells") or []):
        if p and len(p) >= 2:
            unclaimed.add((int(p[0]), int(p[1])))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def man(x1, y1, x2, y2): return abs(x1 - x2) + abs(y1 - y2)

    if not self_terr:
        tx, ty = w // 2, h // 2
    else:
        candidates = []
        for x, y in self_terr:
            for dx, dy in dirs:
                nx, ny = x + dx, y + dy
                if not inb(nx, ny) or (nx, ny) in obstacles: 
                    continue
                if (nx, ny) in self_terr:
                    continue
                if (nx, ny) in opp_terr:
                    val = 6
                elif (nx, ny) in unclaimed:
                    val = 3
                else:
                    continue
                # Prefer stronger captures; tie-break by being closer to the opponent to compress contest.
                score = (-val, man(sx, sy, nx, ny), man(ox, oy, nx, ny), nx, ny)
                candidates.append((score, (nx, ny)))
        if candidates:
            candidates.sort(key=lambda t: t[0])
            tx, ty = candidates[0][1]
        else:
            tx, ty = w // 2, h // 2

    best_step = (0, 0)
    best_key = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        # Slightly prefer moving into opponent territory when possible.
        gain = 1 if (nx, ny) in opp_terr else 0
        key = (-gain, man(nx, ny, tx, ty), (nx - ox)**2 + (ny - oy)**2, nx, ny)
        if best_key is None or key < best_key:
            best_key = key
            best_step = (dx, dy)

    return [int(best_step[0]), int(best_step[1])]