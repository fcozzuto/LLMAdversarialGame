def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    oppx, oppy = observation["opponent_position"]
    selfT = set(tuple(p) for p in (observation.get("self_territory") or []))
    oppT = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    neigh8 = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    neigh4 = [(-1,0),(1,0),(0,-1),(0,1)]

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def dist(ax, ay, bx, by):
        d = ax - bx
        e = ay - by
        if d < 0: d = -d
        if e < 0: e = -e
        return d + e

    def adj_opp(cx, cy):
        for dx, dy in neigh4:
            tx, ty = cx + dx, cy + dy
            if inb(tx, ty) and (tx, ty) in oppT:
                return True
        return False

    def opp_center():
        if oppT:
            sx = sy = 0
            n = len(oppT)
            for px, py in oppT:
                sx += px; sy += py
            return sx // n, sy // n
        return oppx, oppy

    cox, coy = opp_center()

    # Prefer immediate frontier capture; otherwise, push toward opponent control.
    best = (0, 0)
    bestv = -10**18
    for dx, dy in neigh8:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue

        v = 0
        if (nx, ny) in oppT:
            v += 2000  # flipping on entry
        if (nx, ny) in unclaimed:
            v += 120   # claim unclaimed
        if (nx, ny) in selfT:
            v += 10    # maintain territory, less exploratory
        if adj_opp(nx, ny):
            v += 180   # create a strong frontier
        # avoid moving away from opponent and avoid drifting into low-opportunity areas
        v += 50 - 2 * dist(nx, ny, cox, coy)

        # keep from oscillating: slight preference to continue direction based on relative to center
        if dx == 0 and dy == 0:
            v -= 5
        else:
            px, py = nx - x, ny - y
            v += 4 * (1 if px == 0 else 0) + 4 * (1 if py == 0 else 0)

        if v > bestv:
            bestv = v
            best = (dx, dy)

    return [best[0], best[1]]