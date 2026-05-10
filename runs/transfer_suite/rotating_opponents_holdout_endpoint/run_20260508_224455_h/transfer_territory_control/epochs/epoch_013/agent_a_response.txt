def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set(map(tuple, observation.get("obstacles", [])))
    self_t = set(map(tuple, observation.get("self_territory", [])))
    opp_t = set(map(tuple, observation.get("opponent_territory", [])))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells", [])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_score = -10**18

    neigh8 = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        score = 0

        if (nx, ny) in unclaimed:
            score += 220
        elif (nx, ny) in self_t:
            score += 30
        elif (nx, ny) in opp_t:
            score -= 240

        if dx == 0 and dy == 0:
            score -= 8

        # Favor "frontier" moves that open toward unclaimed.
        frontier = 0
        for ddx, ddy in neigh8:
            ax, ay = nx + ddx, ny + ddy
            if inb(ax, ay) and (ax, ay) in unclaimed:
                frontier += 1
        score += 18 * frontier

        # Keep opponent pressure in check: prefer staying farther unless capturing.
        d0 = abs(sx - ox) + abs(sy - oy)
        d1 = abs(nx - ox) + abs(ny - oy)
        score += (d1 - d0) * 6

        # Minor tie-break: approach closest unclaimed when available.
        if unclaimed:
            closest = 10**9
            for cx, cy in unclaimed:
                # quick prune: only consider within radius 4 of move target
                md = abs(cx - nx) + abs(cy - ny)
                if md < closest:
                    closest = md
                    if closest == 0:
                        break
            score += -2 * closest

        if score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]