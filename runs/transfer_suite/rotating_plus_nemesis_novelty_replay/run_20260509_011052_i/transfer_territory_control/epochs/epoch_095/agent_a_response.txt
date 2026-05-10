def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    self_terr = set()
    for p in (observation.get("self_territory", []) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            self_terr.add((int(p[0]), int(p[1])))

    opp_terr = set()
    for p in (observation.get("opponent_territory", []) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            opp_terr.add((int(p[0]), int(p[1])))

    unclaimed = set()
    for p in (observation.get("unclaimed_cells", []) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            unclaimed.add((int(p[0]), int(p[1])))

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    resources = []
    for p in (observation.get("resources", []) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            resources.append((int(p[0]), int(p[1])))

    targets = resources if resources else list(unclaimed) if unclaimed else [(ox, oy)]
    tx, ty = targets[0]
    best_val = -10**18
    best = (0, 0)

    cand = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        if (nx, ny) in opp_terr:
            immediate = 3.0
        elif (nx, ny) in unclaimed:
            immediate = 1.5
        elif (nx, ny) in self_terr:
            immediate = 0.2
        else:
            immediate = 0.4

        dist_opp = abs(nx - ox) + abs(ny - oy)
        near_opp = -0.06 * dist_opp  # push toward them to counterclaim
        dist_t = min(abs(nx - a) + abs(ny - b) for a, b in targets)
        toward_target = -0.12 * dist_t

        penalty_adj = 0.0
        if abs(nx - ox) <= 1 and abs(ny - oy) <= 1 and (nx, ny) not in self_terr:
            penalty_adj = -0.3  # avoid exposing expansion into your territory boundary

        val = immediate + near_opp + toward_target + penalty_adj
        if val > best_val:
            best_val = val
            best = (dx, dy)

    return [int(best[0]), int(best[1])]