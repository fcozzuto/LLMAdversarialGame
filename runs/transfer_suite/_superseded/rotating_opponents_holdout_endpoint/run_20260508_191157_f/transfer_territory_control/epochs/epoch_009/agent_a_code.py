def choose_move(observation):
    sx, sy = observation["self_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    own = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = observation.get("unclaimed_cells") or []
    ox, oy = observation["opponent_position"]
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def king_neighbors(x, y):
        for dx, dy in [(-1, -1),(0, -1),(1, -1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]:
            yield x + dx, y + dy

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    valuable = []
    prefer_opp = observation.get("self_territory_count", 0) < observation.get("opponent_territory_count", 0)
    unclaimed_cells = [tuple(p) for p in unclaimed if inb(p[0], p[1]) and tuple(p) not in obstacles]
    if not unclaimed_cells:
        cand = [p for p in (observation.get("self_territory") or [])]
        target = cand[0] if cand else (sx, sy)
    else:
        for x, y in unclaimed_cells:
            adj_own = any((nx, ny) in own for nx, ny in king_neighbors(x, y) if (nx, ny) != (x, y))
            adj_opp = any((nx, ny) in opp for nx, ny in king_neighbors(x, y) if (nx, ny) != (x, y))
            if adj_own:
                pr = 0 if not prefer_opp else 1
            elif adj_opp:
                pr = 1 if not prefer_opp else 0
            else:
                pr = 2
            valuable.append((pr, dist((sx, sy), (x, y)), x, y))
        valuable.sort()
        target = (valuable[0][2], valuable[0][3])

    best = [0, 0]
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            v = -10**12
        else:
            base = 0
            if (nx, ny) in unclaimed_cells:
                base += 5
            if (nx, ny) in opp:
                base += 7
            if (nx, ny) in own:
                base += 2
            # Encourage advancing frontier and discouraging idle when a useful step exists
            v = base + 0.6 * (-dist((nx, ny), target)) + 0.1 * (-dist((nx, ny), (ox, oy)))
            if dx == 0 and dy == 0:
                v -= 0.2
        if v > best_val:
            best_val = v
            best = [dx, dy]
    return [int(best[0]), int(best[1])]