def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    selfT = set(tuple(p) for p in (observation.get("self_territory") or []))
    oppT = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    neigh = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    def inb(nx, ny): return 0 <= nx < w and 0 <= ny < h
    def clamp_dir(a, b):
        if b > a: return 1
        if b < a: return -1
        return 0
    def man(ax, ay, bx, by):
        d = ax - bx
        if d < 0: d = -d
        e = ay - by
        if e < 0: e = -e
        return d + e

    if not unclaimed:
        tx, ty = (w // 2, h // 2)
    else:
        frontier = []
        if selfT:
            for cx, cy in selfT:
                for dx, dy in ((-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)):
                    nx, ny = cx + dx, cy + dy
                    if inb(nx, ny) and (nx, ny) in unclaimed:
                        frontier.append((nx, ny))
        candidates = frontier if frontier else list(unclaimed)
        best = None; bestd = 10**9
        for tx, ty in candidates:
            d = man(x, y, tx, ty) + (0.5 * man(tx, ty, ox, oy))
            if d < bestd:
                bestd = d; best = (tx, ty)
        tx, ty = best

    desired = (clamp_dir(x, tx), clamp_dir(y, ty))
    best_move = (0, 0); best_score = -10**9

    for dx, dy in neigh:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        score = 0
        if (nx, ny) in unclaimed:
            score += 8
        if (nx, ny) in oppT:
            score += 12
        if selfT:
            for adx, ady in ((-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)):
                ax2, ay2 = nx + adx, ny + ady
                if inb(ax2, ay2) and (ax2, ay2) in selfT:
                    score += 1
        score += -0.35 * man(nx, ny, tx, ty)
        score += 0.20 * man(nx, ny, ox, oy)
        score += 1.5 if (dx, dy) == desired else 0
        if score > best_score:
            best_score = score; best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]