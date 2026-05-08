def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for o in observation.get("obstacles", []) or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            x, y = int(o[0]), int(o[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    role = (observation.get("self_role", "") or "").lower()
    is_evader = ("evader" in role) or ("runner" in role) or ("escape" in role) or ("evade" in role)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def free(x, y): return inb(x, y) and (x, y) not in obstacles

    legal = [(dx, dy) for (dx, dy) in moves if free(sx + dx, sy + dy)]
    if not legal:
        return [0, 0]

    def bfs_dist(startx, starty, limit=12):
        if (startx, starty) == (ox, oy):
            return 0
        qx, qy = [startx], [starty]
        dist = {(startx, starty): 0}
        qi = 0
        while qi < len(qx):
            x, y = qx[qi], qy[qi]; qi += 1
            d = dist[(x, y)]
            if d >= limit:
                continue
            for dx, dy in moves:
                nx, ny = x + dx, y + dy
                if not free(nx, ny):
                    continue
                nd = d + 1
                if (nx, ny) not in dist or nd < dist[(nx, ny)]:
                    dist[(nx, ny)] = nd
                    if (nx, ny) == (ox, oy):
                        return nd
                    qx.append(nx); qy.append(ny)
        return 10**9

    best = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        d = bfs_dist(nx, ny, limit=10)
        # If evader, maximize distance; if pursuer, minimize distance.
        key = d if is_evader else -d
        if best is None:
            best = (key, dx, dy)
        else:
            if key > best[0] or (key == best[0] and (dx, dy) < (best[1], best[2])):
                best = (key, dx, dy)
    return [best[1], best[2]]