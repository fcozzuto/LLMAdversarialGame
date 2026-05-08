def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)

    def xy(p, d=(0, 0)):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            return int(p[0]), int(p[1])
        if isinstance(p, dict) and "x" in p and "y" in p:
            return int(p["x"]), int(p["y"])
        return d

    sx, sy = xy(observation.get("self_position", [0, 0]))
    ox, oy = xy(observation.get("opponent_position", [0, 0]))
    role = observation.get("self_role", "pursuer")

    obstacles = set()
    for o in (observation.get("obstacles") or []):
        x, y = xy(o, None)
        if x is None:
            continue
        if 0 <= x < w and 0 <= y < h:
            obstacles.add((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def bfs_dist(startx, starty, goalx, goaly):
        if (startx, starty) == (goalx, goaly):
            return 0
        qx, qy = [startx], [starty]
        dist = {(startx, starty): 0}
        for i in range(len(qx)):
            x, y = qx[i], qy[i]
            nd = dist[(x, y)] + 1
            for dx, dy in moves:
                nx, ny = x + dx, y + dy
                if not free(nx, ny):
                    continue
                if (nx, ny) not in dist:
                    dist[(nx, ny)] = nd
                    if (nx, ny) == (goalx, goaly):
                        return nd
                    qx.append(nx); qy.append(ny)
        return 999

    best_move = [0, 0]
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            nx, ny = sx, sy
            dx, dy = 0, 0
        d = bfs_dist(nx, ny, ox, oy)
        val = d if role == "evader" else -d
        if best_val is None or val > best_val or (val == best_val and (abs(dx) + abs(dy), dx, dy) < (abs(best_move[0]) + abs(best_move[1]), best_move[0], best_move[1])):
            best_val = val
            best_move = [dx, dy]
    return [int(best_move[0]), int(best_move[1])]