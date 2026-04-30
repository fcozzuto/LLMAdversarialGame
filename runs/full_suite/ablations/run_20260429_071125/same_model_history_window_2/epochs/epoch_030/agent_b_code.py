def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) == 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cd(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    cx, cy = w // 2, h // 2

    if resources:
        best_t = None
        best_v = -10**18
        for rx, ry in resources:
            ds = cd(sx, sy, rx, ry)
            do = cd(ox, oy, rx, ry)
            center = cd(rx, ry, cx, cy)
            # primary: race margin; secondary: self closeness; tertiary: center preference (less travel)
            v = (do - ds) * 1000 - ds * 3 - center
            if v > best_v:
                best_v = v
                best_t = (rx, ry)
        tx, ty = best_t

        best_move = (0, 0)
        best_mv = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            ds2 = cd(nx, ny, tx, ty)
            do2 = cd(ox, oy, tx, ty)
            center2 = cd(nx, ny, cx, cy)
            # new race margin if we move; also discourage stepping away from target
            mv = (do2 - ds2) * 1000 - ds2 * 2 - center2
            # small tie-break: prefer moves that reduce distance to opponent when margins are equal
            if mv == best_mv:
                mv2 = mv - cd(nx, ny, ox, oy) * 0.01
                if mv2 > best_mv:
                    best_mv = mv2
                    best_move = (dx, dy)
            if mv > best_mv:
                best_mv = mv
                best_move = (dx, dy)
        return [int(best_move[0]), int(best_move[1])]

    # No resources: drift to center while not colliding with obstacles; also keep some distance from opponent
    best_move = (0, 0)
    best_v = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        center = cd(nx, ny, cx, cy)
        dist_opp = cd(nx, ny, ox, oy)
        v = -center * 3 + dist_opp
        if v > best_v:
            best_v = v
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]