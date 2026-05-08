def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p is None:
            continue
        x, y = p
        obstacles.add((int(x), int(y)))

    self_role = (observation.get("self_role") or "").lower()
    pursuer = ("purs" in self_role) or ("hunter" in self_role) or ("chaser" in self_role)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def bfs_dist(start, goal):
        if not valid(start[0], start[1]) or not valid(goal[0], goal[1]):
            return None
        if start == goal:
            return 0
        q = [start]
        head = 0
        dist = {start: 0}
        while head < len(q):
            x, y = q[head]
            head += 1
            d = dist[(x, y)] + 1
            for dx, dy in dirs:
                nx, ny = x + dx, y + dy
                if not valid(nx, ny) or (nx, ny) in dist:
                    continue
                dist[(nx, ny)] = d
                if (nx, ny) == goal:
                    return d
                q.append((nx, ny))
        return None

    if not valid(sx, sy):
        return [0, 0]

    best = None
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d = bfs_dist((nx, ny), (ox, oy))
        if d is None:
            score = -10**9 if pursuer else -10**9
        else:
            score = (-d) if pursuer else d
            score += 0.001 * (-(abs(nx - ox) + abs(ny - oy)) if pursuer else (abs(nx - ox) + abs(ny - oy)))
        if best_score is None or score > best_score or (score == best_score and (dx, dy) < best):
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]