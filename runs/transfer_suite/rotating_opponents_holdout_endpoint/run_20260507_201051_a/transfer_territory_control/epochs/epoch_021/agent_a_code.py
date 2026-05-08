def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])[:2]
    obstacles = set(map(tuple, observation.get("obstacles") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))
    st = set(map(tuple, observation.get("self_territory") or []))
    ot = set(map(tuple, observation.get("opponent_territory") or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def neigh8(x, y):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if inb(nx, ny):
                    yield nx, ny, dx, dy

    def neigh4(x, y):
        for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            nx, ny = x + dx, y + dy
            if inb(nx, ny):
                yield nx, ny

    targets = []
    if ot and unclaimed:
        for ex, ey in ot:
            for nx, ny in neigh4(ex, ey):
                if (nx, ny) in unclaimed:
                    targets.append((nx, ny))
    if not targets and st and unclaimed:
        for tx, ty in st:
            for nx, ny in neigh4(tx, ty):
                if (nx, ny) in unclaimed:
                    targets.append((nx, ny))
    if not targets:
        targets = list(unclaimed)

    if not targets:
        for nx, ny, dx, dy in neigh8(sx, sy):
            if (nx, ny) not in obstacles:
                return [dx, dy]
        return [0, 0]

    def score(p):
        px, py = p
        md = abs(px - sx) + abs(py - sy)
        border_bonus = 0
        if px in (0, w - 1) or py in (0, h - 1):
            border_bonus = -1
        if p in st:
            border_bonus += 2
        if p in ot:
            border_bonus -= 1
        return md + border_bonus

    tx, ty = min(targets, key=score)

    best = (0, 0, abs(sx - tx) + abs(sy - ty))
    for nx, ny, dx, dy in neigh8(sx, sy):
        d = abs(nx - tx) + abs(ny - ty)
        if d < best[2]:
            best = (dx, dy, d)
        elif d == best[2]:
            if dx == 0 and dy != 0:
                cand = (0, dx, dy)
            else:
                cand = (1, dx, dy)
            bestcand = (0, best[0], best[1]) if (best[0] == 0 and best[1] != 0) else (1, best[0], best[1])
            if cand < bestcand:
                best = (dx, dy, d)

    return [int(best[0]), int(best[1])]