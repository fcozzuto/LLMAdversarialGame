def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def to_set(key):
        out = set()
        for p in observation.get(key) or []:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h:
                    out.add((x, y))
        return out

    obstacles = to_set("obstacles")
    unclaimed = to_set("unclaimed_cells")
    opp_terr = to_set("opponent_territory")
    self_terr = to_set("self_territory")

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    # 8-dir + stay
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # Heuristic: prefer positions that are closer to us than opponent (territory contest margin),
    # while opportunistically stepping into unclaimed / flipping opponent territory.
    best = None
    best_sc = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            sc = -10**12
        else:
            ds = man(nx, ny, sx, sy)  # always 0/1 but keeps structure
            do = man(nx, ny, ox, oy)
            margin = do - ds  # bigger means opponent is relatively farther
            sc = margin * 10

            if (nx, ny) in unclaimed:
                sc += 20
            if (nx, ny) in opp_terr:
                sc += 10  # flipping gives us control; still prefer distance via margin
            if (nx, ny) in self_terr:
                sc += 6
            # If we can immediately move onto opponent territory, slightly reduce margin weight to allow flips
            if (nx, ny) in opp_terr:
                sc += 5
            # Small bias to progress toward center to avoid being edge-pinned
            cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
            sc -= int((abs(nx - cx) + abs(ny - cy)) * 0.5)

        if sc > best_sc:
            best_sc = sc
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]