def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    targets = []
    for p in (observation.get("resources") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            targets.append((int(p[0]), int(p[1])))
    if not targets:
        for p in (observation.get("unclaimed_cells") or []):
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                targets.append((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    neigh = [(1,0),(-1,0),(0,1),(0,-1)]
    best = None
    best_score = -10**18
    for dx, dy in neigh:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        score = 0
        if nx in (0, w - 1) or ny in (0, h - 1):
            score += 3
        score += - (abs(nx - ox) + abs(ny - oy))
        if targets:
            md = 10**9
            for tx, ty in targets:
                d = abs(nx - tx) + abs(ny - ty)
                if d < md:
                    md = d
            score += -md
        if best is None or score > best_score:
            best_score = score
            best = [dx, dy]
    if best is not None:
        return best
    for dx, dy in neigh:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            return [dx, dy]
    return [0, 0]