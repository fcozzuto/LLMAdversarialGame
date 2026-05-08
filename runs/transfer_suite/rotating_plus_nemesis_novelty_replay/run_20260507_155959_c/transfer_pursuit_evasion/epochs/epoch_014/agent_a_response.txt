def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    sr = str(observation.get("self_role", "")).lower()
    i_am_pursuer = ("purs" in sr) or ("hunter" in sr) or ("tagger" in sr) or ("pursuer" in sr)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def bfs_dist(a, b):
        ax, ay = a
        bx, by = b
        if not inb(ax, ay) or not inb(bx, by):
            return 10**9
        if a == b:
            return 0
        q = [a]
        qi = 0
        dist = {a: 0}
        while qi < len(q):
            x, y = q[qi]
            qi += 1
            nd = dist[(x, y)] + 1
            for dx, dy in deltas:
                nx, ny = x + dx, y + dy
                if inb(nx, ny) and (nx, ny) not in dist:
                    if (nx, ny) == (bx, by):
                        return nd
                    dist[(nx, ny)] = nd
                    q.append((nx, ny))
        return 10**9

    # Deterministic tie-break: fixed move order (deltas).
    best_move = (0, 0)
    best_val = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d = bfs_dist((nx, ny), (ox, oy))
        val = -d if i_am_pursuer else d
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]