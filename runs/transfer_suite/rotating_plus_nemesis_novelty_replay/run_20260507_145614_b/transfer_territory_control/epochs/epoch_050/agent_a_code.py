def choose_move(observation):
    w = int(observation.get("grid_width", 0) or 0)
    h = int(observation.get("grid_height", 0) or 0)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if not (dx == 0 and dy == 0)] + [(0, 0)]
    dirs.sort()

    def to_set(key):
        s = set()
        for p in (observation.get(key) or []):
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                s.add((int(p[0]), int(p[1])))
        return s

    selfT = to_set("self_territory")
    oppT = to_set("opponent_territory")
    unclaimed = to_set("unclaimed_cells")

    resources = set()
    for p in (observation.get("resources") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            resources.add((int(p[0]), int(p[1])))

    best = None
    best_sc = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        sc = 0
        if (nx, ny) in oppT:
            sc += 8000
        if (nx, ny) in unclaimed:
            sc += 5000
        if selfT and (nx, ny) in selfT:
            sc -= 50
        if (nx, ny) in resources:
            sc += 200

        dist_to_opp = abs(nx - ox) + abs(ny - oy)
        sc += 20 * (-dist_to_opp)  # prefer closer to opponent

        if selfT:
            # prefer stepping toward frontier if possible
            frontier = 0
            for px, py in ((nx, ny),):
                for ddx, ddy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                    ax, ay = px + ddx, py + ddy
                    if (ax, ay) in selfT and ((px, py) in unclaimed or (px, py) in oppT):
                        frontier = 1
                        break
            sc += 1500 * frontier

        if sc > best_sc:
            best_sc = sc
            best = (dx, dy)
    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]