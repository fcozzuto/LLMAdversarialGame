def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (w - 1, h - 1)

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p is not None and len(p) == 2:
            obstacles.add((int(p[0]), int(p[1])))

    unclaimed = []
    for p in (observation.get("unclaimed_cells") or []):
        if p is not None and len(p) == 2:
            unclaimed.append((int(p[0]), int(p[1])))

    self_t = set()
    for p in (observation.get("self_territory") or []):
        if p is not None and len(p) == 2:
            self_t.add((int(p[0]), int(p[1])))

    opp_t = set()
    for p in (observation.get("opponent_territory") or []):
        if p is not None and len(p) == 2:
            opp_t.add((int(p[0]), int(p[1])))

    unclaimed_set = set(unclaimed)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h

    # Candidate targets: unclaimed first; if none, try to push into opponent territory via nearest adjacent boundary.
    targets = []
    if unclaimed:
        targets = unclaimed
    else:
        boundary = set()
        for (x, y) in opp_t:
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)):
                nx, ny = x + dx, y + dy
                if inb(nx, ny) and (nx, ny) not in obstacles:
                    boundary.add((nx, ny))
        targets = [p for p in boundary if p in unclaimed_set] or list(boundary) or [(ox, oy)]

    # Deterministic nearest target selection.
    tx, ty = targets[0]
    best = (tx - sx) * (tx - sx) + (ty - sy) * (ty - sy)
    for (x, y) in targets[1:]:
        d = (x - sx) * (x - sx) + (y - sy) * (y - sy)
        if d < best:
            best = d
            tx, ty = x, y

    # Evaluate one-step options to reach the target and (when possible) flip opponent territory by stepping into it.
    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        dist = (tx - nx) * (tx - nx) + (ty - ny) * (ty - ny)

        # Prefer stepping into opponent territory to flip, if it exists as a reachable cell.
        flip = 1 if (nx, ny) in opp_t else 0
        # Avoid getting stuck in own territory wall when unclaimed exists.
        stay_in_self = 1 if (nx, ny) in self_t else 0

        val = dist - 2000 * flip + 5 * stay_in_self
        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]