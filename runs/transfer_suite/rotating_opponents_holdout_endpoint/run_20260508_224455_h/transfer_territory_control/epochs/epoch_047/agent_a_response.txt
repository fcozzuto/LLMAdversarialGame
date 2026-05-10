def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    sx, sy = int(sx), int(sy)
    obstacles = set()
    for c in observation.get("obstacles", []) or []:
        if c is not None and len(c) >= 2 and c[0] is not None and c[1] is not None:
            obstacles.add((int(c[0]), int(c[1])))

    self_set = set(tuple(map(int, p)) for p in (observation.get("self_territory", []) or []))
    opp_set = set(tuple(map(int, p)) for p in (observation.get("opponent_territory", []) or []))
    unclaimed = set(tuple(map(int, p)) for p in (observation.get("unclaimed_cells", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_dx, best_dy = 0, 0
    best_sc = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        if (nx, ny) in opp_set:
            base = 6.0
        elif (nx, ny) in unclaimed:
            base = 3.6
        elif (nx, ny) in self_set:
            base = 1.2
        else:
            base = 2.0

        # Prefer moves that reduce distance to center and (slightly) avoid moving away from it.
        dist_center = abs(nx - cx) + abs(ny - cy)
        dist_from_center = abs(sx - cx) + abs(sy - cy)
        center_score = (dist_from_center - dist_center) * 0.35

        # Heuristic "guard": if opponent territory is adjacent, don't drift away.
        adj_opp = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                tx, ty = nx + ax, ny + ay
                if inb(tx, ty) and (tx, ty) in opp_set:
                    adj_opp += 1
        guard_score = adj_opp * 0.25

        sc = base + center_score + guard_score

        # Deterministic tie-break: prefer (0,0), then lexicographically smaller (dx,dy).
        if sc > best_sc or (sc == best_sc and (best_dx, best_dy) != (0, 0) and (dx, dy) == (0, 0)) or (sc == best_sc and (dx, dy) < (best_dx, best_dy)):
            best_sc = sc
            best_dx, best_dy = dx, dy

    return [int(best_dx), int(best_dy)]