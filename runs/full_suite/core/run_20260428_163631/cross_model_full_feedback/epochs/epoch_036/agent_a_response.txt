def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obst = set()
    for p in observation.get("obstacles", []) or []:
        try:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obst.add((x, y))
        except:
            pass

    resources = []
    for r in observation.get("resources", []) or []:
        try:
            x, y = int(r[0]), int(r[1])
            if inb(x, y) and (x, y) not in obst:
                resources.append((x, y))
        except:
            pass

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    legal = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obst:
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Limit candidates deterministically: nearest few by Manhattan distance from current pos
    if resources:
        resources_sorted = sorted(resources, key=lambda p: (man((sx, sy), p), p[0], p[1]))
        candidates = resources_sorted[:6]
    else:
        candidates = []

    center = (w // 2, h // 2)

    best = None
    best_val = -10**18

    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        myd = man((nx, ny), center)
        oppd = man((nx, ny), (ox, oy))

        if candidates:
            # Prefer moves that get closer to a resource that opponent is not closer to.
            # Score aggregates over top candidates with stronger weight for smaller distances.
            val = 0
            for tx, ty in candidates:
                r = (tx, ty)
                d_me = man((nx, ny), r)
                d_op = man((ox, oy), r)
                # If I'm closer than opponent, strongly prefer; otherwise discourage.
                closer_bonus = (d_op - d_me)
                val += (closer_bonus * 20) - (d_me * 6) - (myd * 1) - (abs(tx) * 0 + abs(ty) * 0)
                # Slightly reward moving onto resource directly
                if d_me == 0:
                    val += 500
            # Also reward increasing distance from opponent when equally good
            val += (oppd * 2)
        else:
            # No visible resources: move to center while keeping distance from opponent
            val = (-myd * 3) + (oppd * 2)

        # Deterministic tie-break by coordinates of the move
        if val > best_val or (val == best_val and (dx, dy) < best):
            best_val = val
            best = (dx, dy)

    return [int(best[0]), int(best[1])]