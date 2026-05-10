def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def ok(x, y):
        return inb(x, y) and (x, y) not in obstacles

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    moves.sort(key=lambda d: (d[0], d[1]))

    sr = str(observation.get("self_role", "")).lower()
    is_evader = ("evader" in sr) or ("runner" in sr) or ("escape" in sr) or ("flee" in sr)

    def bfs_dist(startx, starty, goalx, goaly):
        if (startx, starty) == (goalx, goaly):
            return 0
        if not ok(startx, starty) or not inb(goalx, goaly):
            return 10**9
        qx = [startx]
        qy = [starty]
        head = 0
        dist = {(startx, starty): 0}
        while head < len(qx):
            x = qx[head]
            y = qy[head]
            d = dist[(x, y)]
            head += 1
            if d >= 12:  # limit for speed; grid is tiny anyway
                continue
            for dx, dy in moves:
                nx, ny = x + dx, y + dy
                if ok(nx, ny) and (nx, ny) not in dist:
                    nd = d + 1
                    if (nx, ny) == (goalx, goaly):
                        return nd
                    dist[(nx, ny)] = nd
                    qx.append(nx)
                    qy.append(ny)
        return 10**9

    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d = bfs_dist(nx, ny, ox, oy)
        # primary: path distance to opponent; secondary: Euclidean distance to break ties
        eu2 = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        # Evader maximizes distance; Pursuer minimizes distance.
        if is_evader:
            val = (d, eu2)
            better = best_val is None or val > best_val
        else:
            val = (-d, -eu2)
            better = best_val is None or val > best_val
        if better:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]