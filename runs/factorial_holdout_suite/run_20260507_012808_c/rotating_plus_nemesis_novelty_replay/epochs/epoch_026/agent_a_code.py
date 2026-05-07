def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x = int(r[0]); y = int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_move = [0, 0]

    def mindist(pos, target):
        return abs(pos[0] - target[0]) + abs(pos[1] - target[1])

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        mypos = (nx, ny)

        # Race for the resource where we beat opponent distance most.
        best_for_this = None
        for r in resources:
            myd = mindist(mypos, r)
            opd = mindist((ox, oy), r)
            adv = opd - myd
            # Slightly prefer lower my distance when tied/near-tied.
            val = adv * 100 - myd
            if (best_for_this is None) or (val > best_for_this):
                best_for_this = val

        if (best is None) or (best_for_this > best) or (best_for_this == best and (dx, dy) < (best_move[0], best_move[1])):
            best = best_for_this
            best_move = [dx, dy]

    return best_move