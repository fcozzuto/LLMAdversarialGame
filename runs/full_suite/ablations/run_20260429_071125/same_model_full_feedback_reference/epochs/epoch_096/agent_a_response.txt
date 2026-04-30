def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if resources:
        scored = []
        for rx, ry in resources:
            d1 = man(sx, sy, rx, ry)
            d2 = man(ox, oy, rx, ry)
            # Prefer resources we can reach earlier; otherwise penalize.
            # Primary: (d1 - d2) smaller better, then our distance smaller.
            scored.append((d1 - d2, d1, rx, ry))
        scored.sort()
        # Choose among top candidates deterministically
        best_targets = scored[:3] if len(scored) >= 3 else scored

        best_move = (0, 0)
        best_key = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            # Evaluate move by best target we can improve toward, while staying safer.
            mkey = None
            for (a, d1, rx, ry) in best_targets:
                nd1 = man(nx, ny, rx, ry)
                nd2 = man(ox, oy, rx, ry)
                # Want nd1 - nd2 small and nd1 small; also prefer more distance from opponent.
                key = (nd1 - nd2, nd1, -man(nx, ny, ox, oy), (dx, dy))
                if mkey is None or key < mkey:
                    mkey = key
            if mkey is None:
                continue
            # Prefer not getting closer to opponent if all else ties
            final_key = (mkey[0], mkey[1], mkey[2], mkey[3])
            if best_key is None or final_key < best_key:
                best_key = final_key
                best_move = (dx, dy)
        return [int(best_move[0]), int(best_move[1])]

    # No resources: flee from opponent (deterministically maximize distance)
    best_move = (0, 0)
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        d = man(nx, ny, ox, oy)
        # Tie-break: prefer staying still last, then lexicographically
        key = (-d, dx == 0 and dy == 0, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]