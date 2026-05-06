def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])[:2]
    ox, oy = observation.get("opponent_position", [0, 0])[:2]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    dirs = moves

    def bfs_from(start):
        dist = {(start[0], start[1]): 0}
        q = [start]
        qi = 0
        while qi < len(q):
            x, y = q[qi]
            qi += 1
            d = dist[(x, y)] + 1
            for dx, dy in dirs:
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles and (nx, ny) not in dist:
                    dist[(nx, ny)] = d
                    q.append((nx, ny))
        return dist

    opp_dist = bfs_from((ox, oy))

    best_move = [0, 0]
    best_score = -10**18
    best_self_d = 10**9

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        self_dist = bfs_from((nx, ny))
        score = -10**18
        self_d_for_best = 10**9
        for rx, ry in resources:
            sd = self_dist.get((rx, ry), 10**9)
            od = opp_dist.get((rx, ry), 10**9)
            if sd >= 10**9 and od >= 10**9:
                continue
            margin = od - sd  # positive means we reach earlier
            if margin > score or (margin == score and sd < self_d_for_best):
                score = margin
                self_d_for_best = sd
        if score > best_score or (score == best_score and self_d_for_best < best_self_d):
            best_score = score
            best_self_d = self_d_for_best
            best_move = [dx, dy]

    return best_move