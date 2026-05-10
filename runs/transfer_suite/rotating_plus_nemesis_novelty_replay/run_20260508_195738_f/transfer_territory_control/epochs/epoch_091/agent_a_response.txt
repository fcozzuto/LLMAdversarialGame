def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    obstacles = observation.get("obstacles", []) or []
    obs = set((p[0], p[1]) for p in obstacles)
    opp = set((p[0], p[1]) for p in (observation.get("opponent_territory", []) or []))
    un = set((p[0], p[1]) for p in (observation.get("unclaimed_cells", []) or []))
    selft = set((p[0], p[1]) for p in (observation.get("self_territory", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    nbrs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    frontier = []
    for ux, uy in un:
        for dx, dy in ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)):
            if (ux + dx, uy + dy) in selft:
                frontier.append((ux, uy))
                break

    def manh(x, y):
        return abs(x - sx) + abs(y - sy)

    if frontier:
        tx, ty = min(frontier, key=lambda p: (manh(p[0], p[1]), p[0], p[1]))
    elif un:
        tx, ty = min(un, key=lambda p: (manh(p[0], p[1]), p[0], p[1]))
    elif opp:
        candidates = []
        for px, py in opp:
            for dx, dy in ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)):
                nx, ny = px + dx, py + dy
                if inb(nx, ny) and (nx, ny) not in obs and (nx, ny) not in selft:
                    candidates.append((nx, ny))
        if candidates:
            tx, ty = min(candidates, key=lambda p: (manh(p[0], p[1]), p[0], p[1]))
        else:
            tx, ty = sx, sy
    else:
        tx, ty = sx, sy

    def adj_count(ns, x, y):
        c = 0
        for dx, dy in nbrs:
            if dx == 0 and dy == 0:
                continue
            nx, ny = x + dx, y + dy
            if (nx, ny) in ns:
                c += 1
        return c

    best = (-10**18, (0, 0))
    for dx, dy in nbrs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        base = 0
        if (nx, ny) in un:
            base += 6
        if (nx, ny) in opp:
            base += 10
        if (nx, ny) in selft:
            base += 2
        base += 0.7 * adj_count(un, nx, ny)
        base += 0.4 * adj_count(opp, nx, ny)
        base -= 0.1 * manh(nx, ny)
        base -= 0.03 * (adj_count(obs, nx, ny))
        if base > best[0] or (base == best[0] and (dx, dy) < best[1]):
            best = (base, (dx, dy))
    return [int(best[1][0]), int(best[1][1])]