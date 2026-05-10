def choose_move(observation):
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    sx, sy = int(sx), int(sy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    self_terr = set()
    for c in observation.get("self_territory") or []:
        if c and len(c) >= 2:
            self_terr.add((int(c[0]), int(c[1])))

    opp_terr = set()
    for c in observation.get("opponent_territory") or []:
        if c and len(c) >= 2:
            opp_terr.add((int(c[0]), int(c[1])))

    unclaimed = set()
    for c in observation.get("unclaimed_cells") or []:
        if c and len(c) >= 2:
            unclaimed.add((int(c[0]), int(c[1])))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < W and 0 <= y < H

    def manh(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    neigh8 = dirs
    frontier = []
    if opp_terr and unclaimed:
        for ux, uy in unclaimed:
            for dx, dy in neigh8:
                nx, ny = ux + dx, uy + dy
                if (nx, ny) in opp_terr:
                    frontier.append((ux, uy))
                    break

    # Deterministic target selection
    candidates = frontier if frontier else (list(unclaimed) if unclaimed else list(opp_terr))
    if not candidates:
        return [0, 0]
    candidates.sort(key=lambda t: (manh((sx, sy), t), t[0], t[1]))
    tx, ty = candidates[0]

    best = (None, -10**18)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        d = abs(nx - tx) + abs(ny - ty)
        if (nx, ny) in opp_terr:
            sc = 10000 - 2 * d
        elif (nx, ny) in unclaimed:
            sc = 700 - d
        elif (nx, ny) in self_terr:
            sc = 200 - d
        else:
            sc = 80 - d
        if dx == 0 and dy == 0:
            sc -= 5  # slightly prefer moving toward target
        if sc > best[1] or (sc == best[1] and (dx, dy) < best[0]):
            best = ((dx, dy), sc)

    if best[0] is None:
        return [0, 0]
    return [int(best[0][0]), int(best[0][1])]