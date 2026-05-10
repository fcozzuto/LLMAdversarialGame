def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    px, py = observation.get("opponent_position", (0, 0))

    obstacles = set(map(tuple, observation.get("obstacles", [])))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells", [])))
    self_terr = set(map(tuple, observation.get("self_territory", [])))
    opp_terr_list = observation.get("opponent_territory", []) or []
    opp_terr = set(map(tuple, opp_terr_list))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def free(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def nearest_unclaimed_dist(x, y):
        if not unclaimed:
            return 0
        best = 10**9
        for ux, uy in unclaimed:
            d = abs(x - ux) + abs(y - uy)
            if d < best:
                best = d
        return best

    def opp_adjacent_penalty(x, y):
        pen = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if (nx, ny) in opp_terr:
                    pen += 1
        return pen

    best_move = (0, 0)
    bestv = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        v = 0
        if (nx, ny) in unclaimed:
            v += 140
        if (nx, ny) in opp_terr:
            v += 85  # flipping on entry
        if (nx, ny) in self_terr:
            v -= 3

        # Move pressure: head toward nearest unclaimed frontier
        du = nearest_unclaimed_dist(nx, ny)
        v += max(0, 40 - du) * 3

        # Avoid stepping too close to opponent controlled cells unless capturing
        v -= opp_adjacent_penalty(nx, ny) * (18 if (nx, ny) not in opp_terr else 6)

        # Keep some distance control to prevent immediate counter-flanks
        v -= (abs(nx - px) + abs(ny - py)) * 0.2

        # Prefer valid movement order deterministically
        if v > bestv:
            bestv = v
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]