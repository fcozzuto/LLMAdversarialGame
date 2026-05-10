def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    obstacles = set(map(tuple, observation.get("obstacles") or []))
    self_terr = set(map(tuple, observation.get("self_territory") or []))
    opp_terr = set(map(tuple, observation.get("opponent_territory") or []))
    unclaimed = list(map(tuple, observation.get("unclaimed_cells") or []))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def legal(nx, ny):
        return inb(nx, ny) and (nx, ny) not in obstacles

    def neigh8(x, y):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx or dy:
                    nx, ny = x + dx, y + dy
                    if inb(nx, ny):
                        yield nx, ny

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    targets = []
    if unclaimed:
        for cell in unclaimed:
            x, y = cell
            adj_opp = any(n in opp_terr for n in neigh8(x, y))
            adj_self = any(n in self_terr for n in neigh8(x, y))
            if adj_opp:
                targets.append((0, x, y))
            elif adj_self:
                targets.append((1, x, y))
        if not targets:
            targets = [(2, x, y) for (x, y) in unclaimed]
    else:
        targets = [(2, x, y) for (x, y) in opp_terr] if opp_terr else [(2, sx, sy)]

    targets.sort(key=lambda t: (t[0], man(sx, sy, t[1], t[2]), t[1], t[2]))
    tx, ty = targets[0][1], targets[0][2]

    best = [0, 0]
    best_key = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        # Prefer moves that go toward the target, and slightly prefer stepping near opponent territory
        toward = man(nx, ny, tx, ty)
        adj_opp = 0
        if any(n in opp_terr for n in neigh8(nx, ny)):
            adj_opp = 1
        # Tie-break deterministically by fixed key components
        key = (toward, -adj_opp, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best = [dx, dy]
    return best if legal(sx + best[0], sy + best[1]) else [0, 0]