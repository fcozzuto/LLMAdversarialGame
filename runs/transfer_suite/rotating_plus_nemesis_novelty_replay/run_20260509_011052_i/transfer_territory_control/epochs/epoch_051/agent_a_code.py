def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    self_terr = set((int(p[0]), int(p[1])) for p in (observation.get("self_territory", []) or []))
    opp_terr = set((int(p[0]), int(p[1])) for p in (observation.get("opponent_territory", []) or []))
    unclaimed = set((int(p[0]), int(p[1])) for p in (observation.get("unclaimed_cells", []) or []))
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles", []) or []))

    dirs8 = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def adj4(x, y):
        return [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    best = None
    best_key = None
    for dx, dy in dirs8:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy
            dx, dy = 0, 0
        cell = (nx, ny)

        d_opp = man(nx, ny, ox, oy)
        near_opp = 0
        near_self = 0
        for ax, ay in adj4(nx, ny):
            if (ax, ay) in opp_terr:
                near_opp += 1
            if (ax, ay) in self_terr:
                near_self += 1

        if cell in self_terr:
            base = 0.0
        elif cell in opp_terr:
            base = 2.2 - 0.06 * d_opp
        elif cell in unclaimed:
            base = 1.6 - 0.02 * d_opp
        else:
            base = 0.6 - 0.03 * d_opp

        # Push to frontier while avoiding being flanked: reward adjacency to self, punish adjacency to opp.
        score = base + 0.35 * near_self - 0.55 * near_opp

        key = (-score, d_opp, ny, nx, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best = [dx, dy]

    return best if best is not None else [0, 0]