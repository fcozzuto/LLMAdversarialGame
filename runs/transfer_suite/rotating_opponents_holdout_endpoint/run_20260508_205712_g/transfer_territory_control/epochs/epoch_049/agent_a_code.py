def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for t in observation.get("obstacles") or []:
        obstacles.add((int(t[0]), int(t[1])))

    oppT = set()
    for t in observation.get("opponent_territory") or []:
        oppT.add((int(t[0]), int(t[1])))

    unclaimed = set()
    for t in observation.get("unclaimed_cells") or []:
        unclaimed.add((int(t[0]), int(t[1])))

    res = []
    for t in observation.get("resources") or []:
        try:
            res.append((int(t[0]), int(t[1])))
        except:
            pass

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    best = None
    best_score = -10**9
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        score = 0
        if (nx, ny) in oppT:
            score += 1000
        elif (nx, ny) in unclaimed:
            score += 300

        # Prefer approaching resources if present
        if res:
            md = min(abs(nx - rx) + abs(ny - ry) for rx, ry in res)
            score += max(0, 50 - md)

        # Avoid getting too close to opponent
        d_o = abs(nx - ox) + abs(ny - oy)
        score += -min(200, 20 * max(0, 3 - d_o))

        # Small tie-break to keep deterministic preference order
        score -= (dx + 1) * 3 + (dy + 1)

        if score > best_score:
            best_score = score
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best