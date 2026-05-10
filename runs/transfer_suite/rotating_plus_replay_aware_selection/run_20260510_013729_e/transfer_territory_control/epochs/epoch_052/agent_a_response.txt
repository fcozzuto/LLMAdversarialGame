def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    xp, yp = int(sp[0]), int(sp[1])
    op = observation.get("opponent_position") or [0, 0]
    xo, yo = int(op[0]), int(op[1])

    def to_set(key):
        s = set()
        for p in observation.get(key) or []:
            if isinstance(p, (list, tuple)) and len(p) == 2:
                s.add((int(p[0]), int(p[1])))
        return s

    obstacles = to_set("obstacles")
    unclaimed = to_set("unclaimed_cells")
    myt = to_set("self_territory")
    opt = to_set("opponent_territory")

    cx, cy = (w - 1) // 2, (h - 1) // 2
    neighbors = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    # Pick target deterministically: prefer unclaimed near center and not too close to opponent
    if unclaimed:
        best = None
        best_key = None
        for ux, uy in unclaimed:
            if (ux, uy) in obstacles:
                continue
            dcent = abs(ux - cx) + abs(uy - cy)
            dme = abs(ux - xp) + abs(uy - yp)
            dome = abs(ux - xo) + abs(uy - yo)
            key = (dcent, dme, -dome, ux, uy)
            if best_key is None or key < best_key:
                best_key = key
                best = (ux, uy)
        tx, ty = best
    else:
        # If no unclaimed, move toward opponent territory if possible, else toward center
        if opt:
            best = None
            best_key = None
            for ux, uy in opt:
                if (ux, uy) in obstacles:
                    continue
                key = (abs(ux - xp) + abs(uy - yp), abs(ux - xo) + abs(uy - yo), ux, uy)
                if best_key is None or key < best_key:
                    best_key = key
                    best = (ux, uy)
            tx, ty = best
        else:
            tx, ty = cx, cy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    # Score candidate moves by immediate gain heuristics
    best_move = (0, 0)
    best_score = None
    for dx, dy in neighbors:
        nx, ny = xp + dx, yp + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = xp, yp
            dx, dy = 0, 0
        # Immediate territory effect estimate
        if (nx, ny) in myt:
            gain = 0.1
        elif (nx, ny) in unclaimed:
            gain = 2.0
        elif (nx, ny) in opt:
            gain = 3.0  # flipping on entry is true
        else:
            gain = 0.0

        # Prefer stepping closer to target; slightly prefer keeping distance from opponent
        dcur = abs(xp - tx) + abs(yp - ty)
        dnew = abs(nx - tx) + abs(ny - ty)
        dome_new = abs(nx - xo) + abs(ny - yo)
        score = (-(dnew - dcur), gain, dome_new, -abs(dx) - abs(dy), dx, dy)
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]