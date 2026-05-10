def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    sx, sy = int(sx), int(sy)

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    self_t = observation.get("self_territory") or []
    self_set = set()
    for p in self_t:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            self_set.add((int(p[0]), int(p[1])))

    opp_t = observation.get("opponent_territory") or []
    opp_set = set()
    for p in opp_t:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            opp_set.add((int(p[0]), int(p[1])))

    unclaimed = observation.get("unclaimed_cells") or []
    targets = []
    for p in unclaimed:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if (x, y) not in obs:
                targets.append((x, y))

    if not targets:
        for p in opp_set:
            if p not in obs:
                targets.append(p)
    if not targets:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    deltas = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    # nearest target using Manhattan; deterministic tie-breaking by first found minimum
    def nearest_dist(x, y):
        best = 10**9
        for tx, ty in targets:
            d = abs(tx - x) + abs(ty - y)
            if d < best:
                best = d
        return best

    opp_bonus = set(opp_set)  # local alias
    best_move = [0, 0]
    best_score = -10**18

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        d_to_target = nearest_dist(nx, ny)
        # frontier/expansion: count neighbors that are not obstacles and not already ours
        frontier = 0
        steal = 0
        for ddx in (-1, 0, 1):
            for ddy in (-1, 0, 1):
                if ddx == 0 and ddy == 0:
                    continue
                ax, ay = nx + ddx, ny + ddy
                if inb(ax, ay) and (ax, ay) not in obs:
                    if (ax, ay) not in self_set:
                        frontier += 1
                    if (ax, ay) in opp_bonus:
                        steal += 1

        # Prefer capturing by stepping into opponent territory (since flipping on entry is True)
        enter_opp = 1 if (nx, ny) in opp_bonus else 0

        score = (-d_to_target * 3) + (frontier * 1.2) + (steal * 0.6) + (enter_opp * 5.0)
        # deterministic tie-break: keep first in deltas order
        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move