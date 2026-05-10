def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    sx, sy = int(sx), int(sy)

    obs_cells = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs_cells.add((int(p[0]), int(p[1])))

    self_terr = set()
    for p in observation.get("self_territory", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            self_terr.add((int(p[0]), int(p[1])))

    opp_terr = set()
    for p in observation.get("opponent_territory", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            opp_terr.add((int(p[0]), int(p[1])))

    unclaimed = set()
    for p in observation.get("unclaimed_cells", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            unclaimed.add((int(p[0]), int(p[1])))

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    cand = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = [0, 0]
    best_score = -10**18
    best_tie = 10**18

    # Prefer immediate counterclaim: step into opponent territory if adjacent, else into unclaimed.
    opp_frontier = set()
    if self_terr and opp_terr:
        for (x, y) in opp_terr:
            for dx, dy in [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]:
                if (x + dx, y + dy) in self_terr:
                    opp_frontier.add((x, y))
                    break

    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    ox, oy = int(ox), int(oy)

    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs_cells:
            continue

        if (nx, ny) in opp_terr:
            score = 1000  # direct counterclaim
        elif opp_frontier and (nx, ny) in opp_frontier:
            score = 600
        elif (nx, ny) in unclaimed:
            score = 120
        elif (nx, ny) in self_terr:
            score = 20
        else:
            score = 5  # unknown/other

        # Add small shaping to approach opponent and avoid moving away from its territory.
        dist_opp = abs(nx - ox) + abs(ny - oy)
        score -= dist_opp * 2
        tie = dist_opp

        if score > best_score or (score == best_score and tie < best_tie):
            best_score = score
            best_tie = tie
            best_move = [dx, dy]

    return best_move