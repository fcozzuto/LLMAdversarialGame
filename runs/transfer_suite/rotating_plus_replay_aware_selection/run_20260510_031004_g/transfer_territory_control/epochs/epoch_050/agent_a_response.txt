def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    px, py = observation.get("opponent_position", (0, 0))

    obstacles = set(map(tuple, observation.get("obstacles", [])))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells", [])))
    self_terr = set(map(tuple, observation.get("self_territory", [])))
    opp_terr = set(map(tuple, observation.get("opponent_territory", [])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def free(x, y):
        return inb(x, y) and (x, y) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def neigh_score(x, y):
        # how much we could expand from (x,y)
        s = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                nx, ny = x + ax, y + ay
                if not inb(nx, ny) or (nx, ny) in obstacles:
                    continue
                if (nx, ny) in unclaimed:
                    s += 4
                elif (nx, ny) in self_terr:
                    s += 1
                elif (nx, ny) in opp_terr:
                    s += 3
        return s

    def immediate_risk(x, y):
        # avoid stepping into a cell that lets opponent capture many unclaimed next
        # (approx by how exposed the cell is to opponent proximity)
        d = max(abs(x - px), abs(y - py))
        if d > 2:
            return 0
        # closer means higher risk, but being on opponent territory is still good
        risk = (3 - d) * 2
        if (x, y) in opp_terr:
            risk *= 0.3
        return risk

    # choose deterministically; tie-breaker by smaller dx^2+dy^2 then lexicographic
    best = (float("-inf"), 0, 0, 0)
    best_move = [0, 0]
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue

        val = 0
        if (nx, ny) in unclaimed:
            val += 350
        if (nx, ny) in opp_terr:
            val += 220
        if (nx, ny) in self_terr:
            val += 35

        val += neigh_score(nx, ny) * 2

        # pressure: move to reduce distance to opponent, but don't suicide into risk
        cur_d = max(abs(sx - px), abs(sy - py))
        new_d = max(abs(nx - px), abs(ny - py))
        val += (cur_d - new_d) * 18

        val -= immediate_risk(nx, ny)

        dist2 = dx * dx + dy * dy
        tie = (0 if (nx, ny) in unclaimed else 1, nx, ny)  # prefer unclaimed when tied
        cand = (val, -dist2, -tie[0], tie[1], tie[2])
        if cand > best:
            best = cand
            best_move = [dx, dy]

    return best_move