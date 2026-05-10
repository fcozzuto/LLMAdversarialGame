def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    sx, sy = int(sx), int(sy)
    ox, oy = observation.get("opponent_position", [0, 0])
    ox, oy = int(ox), int(oy)

    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obstacles.add((int(p[0]), int(p[1])))

    self_terr = set((int(p[0]), int(p[1])) for p in (observation.get("self_territory", []) or []))
    opp_terr = set((int(p[0]), int(p[1])) for p in (observation.get("opponent_territory", []) or []))
    unclaimed = set((int(p[0]), int(p[1])) for p in (observation.get("unclaimed_cells", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    opp_count = observation.get("opponent_territory_count", len(opp_terr))
    self_count = observation.get("self_territory_count", len(self_terr))
    cautious = 1 if opp_count > self_count else 0

    best_score = -1e18
    best_move = [0, 0]

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        dist_center = abs(nx - cx) + abs(ny - cy)
        dist_opp = abs(nx - ox) + abs(ny - oy)

        if (nx, ny) in unclaimed:
            base = 6.0
        elif (nx, ny) in opp_terr:
            base = 5.0
        elif (nx, ny) in self_terr:
            base = 3.0
        else:
            base = 1.0

        # Opportunistically flip opponent when ahead; otherwise keep some distance.
        flip_bonus = 0.0
        if (nx, ny) in opp_terr:
            flip_bonus = 3.0 if cautious == 0 else -1.0

        score = base + flip_bonus
        score += (dist_opp * (0.12 if cautious else 0.04))  # stay away when behind
        score += (-dist_center * 0.15)  # bias toward center control

        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move