def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    unclaimed = []
    for p in observation.get("unclaimed_cells") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            unclaimed.append((int(p[0]), int(p[1])))

    opp_terr = []
    for p in observation.get("opponent_territory") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            opp_terr.append((int(p[0]), int(p[1])))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            resources.append((int(p[0]), int(p[1])))

    targets = unclaimed if unclaimed else (resources if resources else opp_terr)
    if not targets:
        return [0, 0]

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Choose deterministic target: closest, then lowest y, then lowest x
    tx, ty = min(targets, key=lambda t: (dist((sx, sy), t), t[1], t[0]))

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                d = abs(nx - tx) + abs(ny - ty)
                # Prefer moves that reduce distance most; tie-break by dx,dy deterministically
                moves.append((d, abs(dx) + abs(dy) == 2, dx, dy))
    if not moves:
        return [0, 0]

    moves.sort(key=lambda m: (m[0], -int(m[1]), m[2], m[3]))
    return [int(moves[0][2]), int(moves[0][3])]