def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    self_t = set(map(tuple, observation.get("self_territory") or []))
    opp_t = set(map(tuple, observation.get("opponent_territory") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))
    obstacles = set(map(tuple, observation.get("obstacles") or []))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def adj_count(ptset, x, y):
        c = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx or dy:
                    if (x + dx, y + dy) in ptset:
                        c += 1
        return c

    # Determine "frontier" target: unclaimed adjacent to our territory, else any unclaimed, else opponent.
    unadj = []
    for ux, uy in unclaimed:
        if adj_count(self_t, ux, uy):
            unadj.append((ux, uy))
    candidates_target = unadj if unadj else (list(unclaimed) if unclaimed else list(opp_t))
    if candidates_target:
        # deterministic: scan sorted by (dist, x, y)
        best = None
        for tx, ty in sorted(candidates_target, key=lambda p: (abs(p[0] - sx) + abs(p[1] - sy), p[0], p[1])):
            best = (tx, ty)
            break
        tx, ty = best
    else:
        tx, ty = sx, sy

    def score_cell(x, y):
        if (x, y) in self_t:
            base = 0.2
        elif (x, y) in opp_t:
            base = 12.0 + 0.8 * adj_count(opp_t, x, y)
        elif (x, y) in unclaimed:
            base = 4.2 + 0.5 * adj_count(self_t, x, y) + 0.25 * adj_count(opp_t, x, y)
        else:
            base = 0.8
        # prefer moving toward target unless already on it
        dist = abs(x - tx) + abs(y - ty)
        base += (-0.25 * dist)
        # avoid getting stuck near obstacles by slight penalty for adjacency
        base -= 0.15 * adj_count(obstacles, x, y)
        return base

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        sc = score_cell(nx, ny)
        if sc > best_score + 1e-9 or (abs(sc - best_score) <= 1e-9 and (dx, dy) < best_move):
            best_score = sc
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]