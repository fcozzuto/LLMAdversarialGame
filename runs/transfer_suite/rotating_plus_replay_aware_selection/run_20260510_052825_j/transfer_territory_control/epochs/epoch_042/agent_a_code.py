def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]

    selfT = set(tuple(p) for p in (observation.get("self_territory") or []))
    oppT = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    neigh4 = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    neigh8 = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if oppT:
        sx = sy = 0
        n = len(oppT)
        for px, py in oppT:
            sx += px
            sy += py
        ocx, ocy = sx // n, sy // n
    else:
        ocx, ocy = ox, oy

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    def adjacent_to_opp(cx, cy):
        for dx, dy in neigh4:
            tx, ty = cx + dx, cy + dy
            if inb(tx, ty) and (tx, ty) in oppT:
                return True
        return False

    best = None
    best_score = -10**9
    best_dist = 10**9

    for dx, dy in neigh8:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue

        score = 0
        if (nx, ny) in oppT:
            score += 3  # likely flip on entry
        elif (nx, ny) in unclaimed:
            score += 2
        elif (nx, ny) in selfT:
            score += 0
        else:
            score += 0

        if adjacent_to_opp(nx, ny):
            score += 1

        # Prefer advancing/contesting toward opponent center
        dist = man(nx, ny, ocx, ocy)
        score -= 0.01 * dist

        # Deterministic tie-breaks
        key = (score, -dist, dx, dy)
        if best is None or key > (best_score, -best_dist, best[0], best[1]):
            best = (dx, dy)
            best_score = score
            best_dist = dist

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]