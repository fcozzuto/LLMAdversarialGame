def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    unclaimed = [tuple(p) for p in (observation.get("unclaimed_cells") or []) if isinstance(p, (list, tuple)) and len(p) >= 2]
    my_terr = set(tuple(p) for p in (observation.get("self_territory") or []) if isinstance(p, (list, tuple)) and len(p) >= 2)
    op_terr = set(tuple(p) for p in (observation.get("opponent_territory") or []) if isinstance(p, (list, tuple)) and len(p) >= 2)

    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def man(a, b):
        return abs(a[0]-b[0]) + abs(a[1]-b[1])

    def nearest_dist(pos, cells, default=9999):
        if not cells:
            return default
        best = default
        for c in cells:
            d = man(pos, c)
            if d < best:
                best = d
        return best

    best_move = (0, 0)
    best_val = -10**18

    # Determine a primary target deterministically
    if unclaimed:
        # Prefer the unclaimed cell that is closest; tie-break by y then x for determinism
        target = min(unclaimed, key=lambda c: (man((sx, sy), c), c[1], c[0]))
    else:
        target = (w//2, h//2)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        cell = (nx, ny)
        val = 0

        # Strongly reward immediate expansion into unclaimed
        if cell in unclaimed:
            val += 5000

        # Slight preference to build on our own territory (avoid unnecessary flips when possible)
        if cell in my_terr:
            val += 50

        # Prefer capturing opponent territory if it's also on our way to unclaimed/center
        if cell in op_terr:
            val += 120

        # Pathing pressure: reduce distance to the chosen target
        val += 10 * (-man(cell, target))

        # Avoid getting too close to opponent when we don't control the cell
        # (deterministic heuristic against immediate counter-claim)
        d_to_op = man(cell, (ox, oy))
        if d_to_op <= 1 and cell not in my_terr:
            val -= 300

        # If no unclaimed, also prefer moves that increase distance from self to opponent control edge
        if not unclaimed:
            val += 5 * (d_to_op)

        # Deterministic tie-break: prefer lexicographically smaller move among equals
        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]