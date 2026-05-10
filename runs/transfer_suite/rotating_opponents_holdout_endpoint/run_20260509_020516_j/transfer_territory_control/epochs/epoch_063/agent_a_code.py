def choose_move(observation):
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def inb(x, y):
        return 0 <= x < W and 0 <= y < H

    def to_set(v):
        s = set()
        if v:
            for p in v:
                if p and len(p) >= 2:
                    x, y = int(p[0]), int(p[1])
                    if inb(x, y):
                        s.add((x, y))
        return s

    obstacles = to_set(observation.get("obstacles"))
    unclaimed = to_set(observation.get("unclaimed_cells"))
    my_t = to_set(observation.get("self_territory"))
    opp_t = to_set(observation.get("opponent_territory"))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Build deterministic targets: unclaimed cells adjacent to opponent territory; else nearest unclaimed; else opponent.
    targets = []
    if opp_t and unclaimed:
        for x, y in sorted(opp_t):
            for dx, dy in dirs:
                nx, ny = x + dx, y + dy
                if (nx, ny) in unclaimed:
                    targets.append((nx, ny))
        targets = list(dict.fromkeys(targets))
    if not targets:
        if unclaimed:
            # Pick a deterministic "best" unclaimed by (distance from self, then sum coords)
            cx = (W - 1) // 2
            cy = (H - 1) // 2
            best = None
            for x, y in sorted(unclaimed):
                d = man(sx, sy, x, y)
                tie = abs(x - cx) + abs(y - cy)
                key = (d, tie, x, y)
                if best is None or key < best[0]:
                    best = (key, (x, y))
            targets = [best[1]] if best else []
    if not targets:
        targets = [(ox, oy)]

    def cell_value(x, y):
        if (x, y) in obstacles:
            return -10**9
        v = 0
        if (x, y) in unclaimed:
            v += 80
        if (x, y) in my_t:
            v += 15
        if opp_t and (x, y) in opp_t:
            v -= 5
        # Encourage moving closer to chosen target(s)
        dmin = None
        for tx, ty in targets:
            d = man(x, y, tx, ty)
            if dmin is None or d < dmin:
                dmin = d
        v += 40 - 5 * dmin
        return v

    best_dir = (0, 0)
    best_val = cell_value(sx, sy)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        v = cell_value(nx, ny)
        if v > best_val or (v == best_val and (dx, dy) < best_dir):
            best_val = v
            best_dir = (dx, dy)
    return [int(best_dir[0]), int(best_dir[1])]