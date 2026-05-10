def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    self_territory = set((int(p[0]), int(p[1])) for p in (observation.get("self_territory", []) or []))
    opp_territory = set((int(p[0]), int(p[1])) for p in (observation.get("opponent_territory", []) or []))
    unclaimed = set((int(p[0]), int(p[1])) for p in (observation.get("unclaimed_cells", []) or []))
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles", []) or []))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs4 = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    dirs8 = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    opp_list = list(opp_territory) if opp_territory else [(int(ox), int(oy))]

    def manhattan(px, py):
        best = 10**9
        for ax, ay in opp_list:
            d = abs(ax - px) + abs(ay - py)
            if d < best:
                best = d
        return best

    def adj_count(x, y, S):
        c = 0
        for dx, dy in dirs4:
            nx, ny = x + dx, y + dy
            if (nx, ny) in S:
                c += 1
        return c

    # Aggressive territory flipping + deterministic tie-break toward closer/safer forward targets
    best_move = [0, 0]
    best_score = -10**18
    for dx, dy in dirs8:
        nx, ny = int(sx + dx), int(sy + dy)
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue

        if (nx, ny) in opp_territory:
            base = 120.0
        elif (nx, ny) in unclaimed:
            base = 18.0
        elif (nx, ny) in self_territory:
            base = 2.0
        else:
            base = 5.0  # still useful if flipping not possible; likely edge pressure

        my_adj = adj_count(nx, ny, self_territory)
        opp_adj = adj_count(nx, ny, opp_territory)

        # Encourage entering opponent territory near our cluster, or expanding unclaimed adjacent to us
        score = base + 3.5 * my_adj + 1.2 * opp_adj

        # Maintain pressure without over-committing: prefer moves that reduce distance to opponent slightly
        d = manhattan(nx, ny)
        score += -0.9 * d

        # Tiny deterministic tie-break: favor moves that increase x then y
        score += 0.001 * (nx * 0.3 + ny * 0.7)

        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]