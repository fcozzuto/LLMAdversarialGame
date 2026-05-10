def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    self_terr = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_terr = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = [tuple(p) for p in (observation.get("unclaimed_cells") or [])]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    t = int(observation.get("turn_index", 0)) % 9
    dirs = dirs[t:] + dirs[:t]

    if (sx, sy) in obstacles:
        return [0, 0]

    cx, cy = (w - 1) // 2, (h - 1) // 2

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    if unclaimed:
        cand = sorted(unclaimed, key=lambda p: (man(sx, sy, p[0], p[1]) - man(ox, oy, p[0], p[1]), man(sx, sy, p[0], p[1]), p[0], p[1]))
        targets = cand[:min(24, len(cand))]
    else:
        targets = []
        for x in range(w):
            for y in range(h):
                if (x, y) not in obstacles and (x, y) not in self_terr and (x, y) not in opp_terr:
                    targets.append((x, y))
        if not targets:
            targets = [p for p in (observation.get("opponent_territory") or []) if tuple(p) not in obstacles]
        if not targets:
            targets = [(cx, cy)]

    target = min(targets, key=lambda p: (man(sx, sy, p[0], p[1]) - man(ox, oy, p[0], p[1]), man(sx, sy, p[0], p[1]), p[0], p[1]))

    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue

        dist_self = man(nx, ny, target[0], target[1])
        dist_opp = man(ox, oy, target[0], target[1])

        if (nx, ny) in unclaimed:
            gain = 120
        elif (nx, ny) in self_terr:
            gain = 10
        elif (nx, ny) in opp_terr:
            gain = 55
        else:
            gain = 22

        edge_bias = 3 if (nx == 0 or ny == 0 or nx == w - 1 or ny == h - 1) else 0
        center_bias = -man(nx, ny, cx, cy) // 2

        score = (gain
                 + (dist_self * -6)
                 + (dist_opp - man(ox, oy, nx, ny)) * 3
                 + edge_bias
                 + center_bias)

        if score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]