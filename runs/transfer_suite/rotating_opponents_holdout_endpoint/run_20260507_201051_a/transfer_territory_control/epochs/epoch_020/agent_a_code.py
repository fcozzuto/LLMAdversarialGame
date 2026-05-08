def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])[:2]
    ox, oy = observation.get("opponent_position", [0, 0])[:2]

    obstacles = set(map(tuple, observation.get("obstacles") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))
    st = set(map(tuple, observation.get("self_territory") or []))
    ot = set(map(tuple, observation.get("opponent_territory") or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def neigh4(x, y):
        return [(x-1, y), (x+1, y), (x, y-1), (x, y+1)]

    targets = []
    for ex, ey in ot:
        for nx, ny in neigh4(ex, ey):
            if inb(nx, ny) and (nx, ny) in unclaimed:
                targets.append((nx, ny))
    if not targets:
        for tx, ty in st:
            for nx, ny in neigh4(tx, ty):
                if inb(nx, ny) and (nx, ny) in unclaimed:
                    targets.append((nx, ny))
    if not targets:
        targets = list(unclaimed)

    if not targets:
        for nx, ny in neigh4(sx, sy):
            if inb(nx, ny):
                dx, dy = nx - sx, ny - sy
                return [int(dx), int(dy)]
        return [0, 0]

    tx, ty = min(targets, key=lambda p: abs(p[0] - sx) + abs(p[1] - sy))
    options = [(nx, ny) for nx, ny in neigh4(sx, sy) if inb(nx, ny)]
    if not options:
        return [0, 0]

    options.sort(key=lambda p: (abs(p[0] - tx) + abs(p[1] - ty), abs(p[0] - ox) + abs(p[1] - oy)))
    nx, ny = options[0]
    return [int(nx - sx), int(ny - sy)]