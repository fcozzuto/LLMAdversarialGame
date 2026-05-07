def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    ap = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(ap[0]), int(ap[1])

    obstacles = set()
    for o in observation.get("obstacles", []) or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            x, y = int(o[0]), int(o[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def mdist(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = (0, 0)
    best_val = -10**18

    # Heuristic: maximize "we arrive sooner than opponent" for the best resource.
    # Value for a resource t from our candidate next position n:
    #   opp_adv = (d_opp - d_self_next)
    # Also add a small term to break ties toward closer resources.
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        move_val = -10**18
        for tx, ty in resources:
            d_self = mdist(nx, ny, tx, ty)
            d_opp = mdist(ox, oy, tx, ty)
            # If we're on the resource now, prioritize heavily.
            if d_self == 0:
                val = 10**9 + d_opp
            else:
                val = (d_opp - d_self) * 100 - d_self + (1 if (d_opp - d_self) > 0 else 0) * 5
            if val > move_val:
                move_val = val

        # If all targets are equally bad, prefer moves that reduce our average distance.
        if move_val == -10**18:
            avg = 0
            for tx, ty in resources:
                avg += mdist(nx, ny, tx, ty)
            move_val = -avg

        if move_val > best_val:
            best_val = move_val
            best = (dx, dy)

    return [int(best[0]), int(best[1])]