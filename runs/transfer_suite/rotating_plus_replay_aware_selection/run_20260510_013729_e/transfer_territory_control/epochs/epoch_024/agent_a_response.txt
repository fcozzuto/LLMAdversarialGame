def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    x, y = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])

    obstacles = set(map(tuple, observation.get("obstacles", [])))
    self_ter = set(map(tuple, observation.get("self_territory", [])))
    opp_ter = set(map(tuple, observation.get("opponent_territory", [])))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells", [])))
    cells = observation.get("unclaimed_cells", [])  # keep present for schema

    def inb(a, b):
        return 0 <= a < w and 0 <= b < h

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    # Compute best immediate move by deterministic scoring.
    def score_cell(nx, ny):
        if (nx, ny) in obstacles:
            return -10**9
        if (nx, ny) in self_ter:
            base = 5  # keep territory stable
        elif (nx, ny) in unclaimed:
            base = 20
        elif (nx, ny) in opp_ter:
            base = 12  # flipping can be good, but slightly less than unclaimed
        else:
            base = 8

        # Prefer expanding our frontier: move that increases adjacency to our territory.
        adj_self = 0
        adj_opp = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                tx, ty = nx + ax, ny + ay
                if inb(tx, ty):
                    if (tx, ty) in self_ter:
                        adj_self += 1
                    if (tx, ty) in opp_ter:
                        adj_opp += 1

        # Push toward opponent side to break their edge claims.
        dist_opp = abs(nx - ox) + abs(ny - oy)

        # Small penalty for getting too close to obstacles is already handled by obstacle check;
        # add mild penalty for moving into tight area without progress.
        tight = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                tx, ty = nx + ax, ny + ay
                if inb(tx, ty) and (tx, ty) in obstacles:
                    tight += 1

        # Encourage capturing unclaimed near our frontier and discourage adjacency to opponents without capture.
        frontier_bonus = adj_self * 6
        capture_bonus = (20 if (nx, ny) in unclaimed else 0) + (10 if (nx, ny) in opp_ter else 0)

        return base + frontier_bonus + capture_bonus - (dist_opp * 0.9) + (adj_opp * 1.0) - (tight * 2.0)

    best_move = [0, 0]
    best_score = score_cell(x, y)
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        sc = score_cell(nx, ny)
        if sc > best_score + 1e-9:
            best_score = sc
            best_move = [dx, dy]
        elif abs(sc - best_score) <= 1e-9:
            # Deterministic tie-break: prefer moves that reduce distance to opponent, then lexicographic.
            dcur = abs(x - ox) + abs(y - oy)
            dnew = abs(nx - ox) + abs(ny - oy)
            bcur = (dcur, best_move[0], best_move[1])
            bnew = (dnew, dx, dy)
            if bnew < bcur:
                best_move = [dx, dy]
    return [int(best_move[0]), int(best_move[1])]