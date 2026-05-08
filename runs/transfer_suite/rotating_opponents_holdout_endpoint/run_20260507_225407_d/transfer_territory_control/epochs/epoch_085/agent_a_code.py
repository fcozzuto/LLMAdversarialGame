def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    unclaimed = []
    for p in (observation.get("unclaimed_cells") or []):
        if p and len(p) >= 2:
            unclaimed.append((int(p[0]), int(p[1])))

    self_terr = set()
    for p in (observation.get("self_territory") or []):
        if p and len(p) >= 2:
            self_terr.add((int(p[0]), int(p[1])))

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    best = None
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        val = 0
        if (nx, ny) == (ox, oy):
            val -= 10**9
        if (nx, ny) in unclaimed:
            val += 10**6
        if (nx, ny) in self_terr:
            val += 200
        if unclaimed:
            # Encourage moving closer to the closest unclaimed cell deterministically
            d = min(abs(nx - ux) + abs(ny - uy) for (ux, uy) in unclaimed)
            val += 50 - d
        # Small deterministic preference to keep stability near center of our territory
        if not unclaimed:
            val += 1 if (nx, ny) in self_terr else 0
        if best_val is None or val > best_val:
            best_val = val
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best