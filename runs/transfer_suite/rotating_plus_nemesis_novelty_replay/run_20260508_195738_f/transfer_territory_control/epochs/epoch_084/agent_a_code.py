def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    obstacles = observation.get("obstacles", []) or []
    obs = set((p[0], p[1]) for p in obstacles)
    opp = set((p[0], p[1]) for p in (observation.get("opponent_territory", []) or []))
    un = set((p[0], p[1]) for p in (observation.get("unclaimed_cells", []) or []))
    selft = set((p[0], p[1]) for p in (observation.get("self_territory", []) or []))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def adj_to_ours(x, y):
        for ddx in (-1, 0, 1):
            for ddy in (-1, 0, 1):
                if ddx == 0 and ddy == 0:
                    continue
                if (x + ddx, y + ddy) in selft:
                    return True
        return False

    edge_un = [(x, y) for (x, y) in un if x in (0, w - 1) or y in (0, h - 1)]
    if edge_un:
        ex, ey = min(edge_un, key=lambda p: abs(p[0] - sx) + abs(p[1] - sy))
    else:
        ex, ey = (sx, sy)

    best = -10**9
    best_move = [0, 0]
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        gain = 0
        if (nx, ny) in selft:
            gain += 2
        elif (nx, ny) in un:
            gain += 6
        elif (nx, ny) in opp:
            gain += 2  # flipping on entry, but lower than safe expansion

        if adj_to_ours(nx, ny):
            gain += 4 if (nx, ny) in un else 2

        d_edge = abs(nx - ex) + abs(ny - ey)
        d_here = abs(sx - ex) + abs(sy - ey)
        gain += (d_here - d_edge) * 1.2

        # Prefer reducing distance to unclaimed even if not edge
        if un:
            ux, uy = min(un, key=lambda p: abs(p[0] - nx) + abs(p[1] - ny))
            gain += max(0, (abs(ux - sx) + abs(uy - sy)) - (abs(ux - nx) + abs(uy - ny))) * 0.6

        if gain > best:
            best = gain
            best_move = [dx, dy]
    return best_move