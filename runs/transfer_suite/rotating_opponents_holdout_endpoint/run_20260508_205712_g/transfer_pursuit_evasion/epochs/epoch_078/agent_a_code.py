def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    obstacles = set()
    for a in observation.get("obstacles") or []:
        if isinstance(a, (list, tuple)) and len(a) >= 2:
            x, y = int(a[0]), int(a[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    sr = str(observation.get("self_role") or "").lower()
    self_is_pursuer = any(k in sr for k in ("pursuer", "hunter", "chaser"))

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def bfs_dist(src, goal):
        if src == goal:
            return 0
        gx, gy = goal
        if not inb(gx, gy):
            return None
        q = [src]
        dist = {src: 0}
        for x, y in q:
            d = dist[(x, y)] + 1
            for dx, dy in moves:
                nx, ny = x + dx, y + dy
                if inb(nx, ny) and (nx, ny) not in dist:
                    if (nx, ny) == (gx, gy):
                        return d
                    dist[(nx, ny)] = d
                    q.append((nx, ny))
        return None

    best_move = (0, 0)
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d = bfs_dist((nx, ny), (ox, oy))
        if d is None:
            d = 999999
        # Pursuer: minimize distance. Evader: maximize distance.
        val = d if not self_is_pursuer else -d
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]