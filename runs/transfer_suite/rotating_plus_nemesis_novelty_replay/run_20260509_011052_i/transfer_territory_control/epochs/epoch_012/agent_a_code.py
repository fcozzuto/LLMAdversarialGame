def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0)) or (0, 0)
    ox, oy = observation.get("opponent_position", (0, 0)) or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obstacles.add((int(p[0]), int(p[1])))

    self_terr = set()
    for p in (observation.get("self_territory", []) or []):
        if isinstance(p, (list, tuple)) and len(p) == 2:
            self_terr.add((int(p[0]), int(p[1])))

    unclaimed = []
    for p in (observation.get("unclaimed_cells", []) or []):
        if isinstance(p, (list, tuple)) and len(p) == 2:
            unclaimed.append((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]

    target = None
    best = None
    if unclaimed:
        for ux, uy in unclaimed:
            touches = False
            for ax, ay in ((-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)):
                if (ux + ax, uy + ay) in self_terr:
                    touches = True
                    break
            if touches:
                d = (ux - sx) * (ux - sx) + (uy - sy) * (uy - sy)
                if best is None or d < best:
                    best = d
                    target = (ux, uy)
        if target is None:
            for ux, uy in unclaimed:
                d = (ux - sx) * (ux - sx) + (uy - sy) * (uy - sy)
                if best is None or d < best:
                    best = d
                    target = (ux, uy)

    if target is None:
        target = (ox, oy)

    tx, ty = target
    candidates = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if dx == 0 and dy == 0:
            ok = inb(nx, ny)
        else:
            ok = inb(nx, ny) and (nx, ny) not in obstacles
        if ok:
            dist = (tx - nx) * (tx - nx) + (ty - ny) * (ty - ny)
            toward_opp = -((ox - nx) * (ox - nx) + (oy - ny) * (oy - ny))
            candidates.append((dist, -toward_opp, dx, dy))
    if not candidates:
        return [0, 0]
    candidates.sort()
    return [int(candidates[0][2]), int(candidates[0][3])]