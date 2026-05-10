def choose_move(observation):
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    self_terr = set()
    for c in observation.get("self_territory", []) or []:
        if c and len(c) >= 2:
            self_terr.add((int(c[0]), int(c[1])))

    opp_terr = set()
    for c in observation.get("opponent_territory", []) or []:
        if c and len(c) >= 2:
            opp_terr.add((int(c[0]), int(c[1])))

    unclaimed = set()
    for c in observation.get("unclaimed_cells", []) or []:
        if c and len(c) >= 2:
            unclaimed.add((int(c[0]), int(c[1])))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < W and 0 <= y < H

    def clamp(v, lo, hi):
        return lo if v < lo else hi if v > hi else v

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    best = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        if unclaimed:
            d_un = min(dist((nx, ny), c) for c in unclaimed)
        else:
            d_un = 999

        d_opp = dist((nx, ny), (ox, oy))
        toward_center = dist((nx, ny), ((W - 1) // 2, (H - 1) // 2))

        cell_type = 0
        if (nx, ny) in unclaimed:
            cell_type = 3
        elif (nx, ny) in opp_terr:
            cell_type = 2
        elif (nx, ny) in self_terr:
            cell_type = 1

        # Prefer grabbing unclaimed; otherwise pressure opponent territory; avoid moving too close if no targets.
        val = (cell_type * 1000) - (d_un * 8) + (d_opp if cell_type == 2 else -d_opp * 2) - toward_center * 1
        # Deterministic tie-break: lexicographic on move.
        key = (-val, dx, dy)
        if best is None or key < best[0]:
            best = (key, [dx, dy])

    if best is None:
        return [0, 0]
    return best[1]