def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    occ = {(p[0], p[1]) for p in obstacles}

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def local_obstacle_pen(x, y):
        if (x, y) in occ:
            return 10**9
        pen = 0
        for ax, ay in [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)]:
            if (x+ax, y+ay) in occ:
                pen += 8 if (ax == 0 or ay == 0) else 5
        return pen

    if not resources:
        return [0, 0]

    best = (0, 0)
    best_sc = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in occ:
            continue

        pen = local_obstacle_pen(nx, ny)
        if pen >= 10**8:
            continue

        # Choose the move maximizing our advantage over the opponent for a single resource.
        sc = -pen * 3
        for rx, ry in resources:
            if (rx, ry) in occ:
                continue
            dm = dist(nx, ny, rx, ry)
            do = dist(ox, oy, rx, ry)
            # Positive when we are closer; prioritize winning over short distance.
            adv = do - dm
            # If we are behind, strongly discourage moves that keep us behind.
            behind = 1 if adv < 0 else 0
            s = adv * 70 - dm * 2 - behind * 35
            # Small capture urgency.
            if dm == 0:
                s += 200
            elif dm == 1:
                s += 40
            sc = max(sc, s - pen * 0.5)

        if sc > best_sc:
            best_sc = sc
            best = (dx, dy)

    # Fallback if all moves were blocked: stay.
    if best_sc == -10**18:
        return [0, 0]
    return [int(best[0]), int(best[1])]