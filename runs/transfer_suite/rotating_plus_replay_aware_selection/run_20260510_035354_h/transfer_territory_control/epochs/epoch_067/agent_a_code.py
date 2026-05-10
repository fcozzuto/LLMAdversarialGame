def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    ax, ay = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    unclaimed = observation.get("unclaimed_cells") or []
    obstacles = observation.get("obstacles") or []
    self_terr = observation.get("self_territory") or []
    opp_terr = observation.get("opponent_territory") or []

    uset = {(p[0], p[1]) for p in self_terr if isinstance(p, (list, tuple)) and len(p) >= 2}
    ucell = {(p[0], p[1]) for p in unclaimed if isinstance(p, (list, tuple)) and len(p) >= 2}
    oset = {(p[0], p[1]) for p in opp_terr if isinstance(p, (list, tuple)) and len(p) >= 2}
    obset = {(p[0], p[1]) for p in obstacles if isinstance(p, (list, tuple)) and len(p) >= 2}

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    def neigh4(x, y):
        return [(x+1,y), (x-1,y), (x,y+1), (x,y-1)]

    targets = ucell if ucell else set()
    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    best = (0, 0)
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = ax + dx, ay + dy
        if not inb(nx, ny): 
            continue
        if (nx, ny) in obset:
            continue

        cell_type = 0
        if (nx, ny) in uset:
            cell_type = 0
        elif (nx, ny) in ucell:
            cell_type = 2
        elif (nx, ny) in oset:
            cell_type = 3  # can steal by flipping on entry

        frontier = 0
        for xx, yy in neigh4(nx, ny):
            if not inb(xx, yy) or (xx, yy) in obset:
                continue
            if (xx, yy) in ucell:
                frontier += 1
            elif (xx, yy) in oset:
                frontier += 0  # just a neutral boundary
            elif (xx, yy) in uset:
                frontier -= 0  # stable

        if targets:
            dmin = 10**9
            for tx, ty in targets:
                d = man(nx, ny, tx, ty)
                if d < dmin: dmin = d
        else:
            dmin = man(nx, ny, ox, oy)

        # Prefer capturing unclaimed and creating a boundary; penalize being pulled into opponent territory too much.
        val = cell_type * 10 + frontier * 3 - dmin - (1 if (nx, ny) in oset else 0) * 2
        # Tie-break deterministically by order of moves.
        if val > best_val:
            best_val = val
            best = (dx, dy)

    return [int(best[0]), int(best[1])]