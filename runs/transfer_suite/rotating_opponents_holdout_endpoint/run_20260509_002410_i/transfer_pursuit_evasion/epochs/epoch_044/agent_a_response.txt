def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    self_role = str(observation.get("self_role") or "").lower()
    opponent_role = str(observation.get("opponent_role") or "").lower()
    is_evader = (self_role == "evader") or ("evader" in self_role) or (opponent_role == "pursuer")

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def blocked(x, y):
        return (x, y) in obstacles

    def bfs_dist(start, goal):
        if start == goal:
            return 0
        gx, gy = goal
        if not inb(gx, gy) or blocked(gx, gy):
            return 10**9
        q = [start]
        dist = {start: 0}
        qi = 0
        while qi < len(q):
            x, y = q[qi]
            qi += 1
            d = dist[(x, y)] + 1
            for dx, dy in deltas:
                nx, ny = x + dx, y + dy
                if not inb(nx, ny) or blocked(nx, ny):
                    continue
                if (nx, ny) not in dist:
                    if (nx, ny) == (gx, gy):
                        return d
                    dist[(nx, ny)] = d
                    q.append((nx, ny))
        return 10**9

    candidates = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and not blocked(nx, ny):
            d = bfs_dist((nx, ny), (ox, oy))
            candidates.append((d, dx, dy))

    if not candidates:
        return [0, 0]

    if is_evader:
        best = max(candidates, key=lambda t: (t[0], -abs(t[1]) - abs(t[2]), -t[1], -t[2]))
    else:
        best = min(candidates, key=lambda t: (t[0], abs(t[1]) + abs(t[2]), t[1], t[2]))

    return [int(best[1]), int(best[2])]