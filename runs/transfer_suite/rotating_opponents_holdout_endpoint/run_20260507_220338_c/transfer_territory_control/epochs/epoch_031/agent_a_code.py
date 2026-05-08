def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (sx, sy)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        obstacles.add((int(p[0]), int(p[1])))

    myset = set((int(p[0]), int(p[1])) for p in (observation.get("self_territory") or []))
    unclaimed = set((int(p[0]), int(p[1])) for p in (observation.get("unclaimed_cells") or []))
    oppset = set((int(p[0]), int(p[1])) for p in (observation.get("opponent_territory") or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    base = myset if myset else {(sx, sy)}
    dirs8 = [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)]

    # Candidates: unclaimed adjacent to our territory (defensive expansion / anti-counterclaim)
    cand = []
    for x, y in base:
        for dx, dy in dirs8:
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and (nx, ny) in unclaimed:
                cand.append((nx, ny))
    if not cand:
        for dx, dy in dirs8:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) in unclaimed:
                cand.append((nx, ny))
    if not cand:
        return [0, 0]

    cx, cy = w // 2, h // 2

    # Score: prioritize far from opponent, slight preference toward center to keep pressure
    def mindist_to_opp(px, py):
        if oppset:
            best = 10**9
            for ax, ay in oppset:
                d = abs(px - ax) + abs(py - ay)
                if d < best:
                    best = d
            return best
        return abs(px - ox) + abs(py - oy)

    best_cell = None
    best_key = None
    for x, y in cand:
        if (x, y) in obstacles:
            continue
        dopp = mindist_to_opp(x, y)
        # prefer keeping away from opponent while still approaching the middle
        center_adv = -(abs(x - cx) + abs(y - cy))
        # deterministic tie-break using coordinates
        key = (-dopp, -center_adv, y, x)
        if best_key is None or key < best_key:
            best_key = key
            best_cell = (x, y)

    if best_cell is None:
        return [0, 0]

    tx, ty = best_cell
    if (tx, ty) == (sx, sy):
        return [0, 0]

    # Choose step that reduces distance to target; avoid obstacles if possible
    best_move = (0, 0)
    best_dist = abs(tx - sx) + abs(ty - sy) + 10
    for dx, dy in dirs8 + [(0, 0)]:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        dist = abs(tx - nx) + abs(ty - ny)
        if dist < best_dist:
            best_dist = dist
            best_move = (dx, dy)
        elif dist == best_dist:
            if (dy, dx) < (best_move[1], best_move[0]):
                best_move = (dx, dy)

    if best_move == (0, 0):
        # If all blocked, stay (engine will keep us in place)
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]