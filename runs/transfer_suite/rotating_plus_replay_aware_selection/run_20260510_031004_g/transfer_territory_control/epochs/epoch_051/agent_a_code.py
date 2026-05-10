def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    px, py = observation.get("opponent_position", [0, 0])

    obstacles = set(map(tuple, observation.get("obstacles", []) or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells", []) or []))
    self_terr = set(map(tuple, observation.get("self_territory", []) or []))
    opp_terr = set(map(tuple, observation.get("opponent_territory", []) or []))

    dirs = [(-1, -1), (0, -1), (1, -1),
            (-1, 0), (0, 0), (1, 0),
            (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def free(x, y):
        return inb(x, y) and (x, y) not in obstacles

    best = (0, 0)
    best_val = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue

        dist_opp = abs(nx - px) + abs(ny - py)
        dist_self = abs(nx - sx) + abs(ny - sy)

        val = 0
        if (nx, ny) in opp_terr:
            val += 520  # high value for flipping on entry
            val += 60 * (8 - min(dist_opp, 8))
        elif (nx, ny) in unclaimed:
            val += 360
            val += 20 * (8 - min(dist_opp, 8))
        elif (nx, ny) in self_terr:
            val += 120

        # Prefer moves that progress into opponent vicinity and avoid getting stuck
        val += 18 * (8 - min(dist_opp, 8))
        val -= 6 * dist_self

        # If we can’t flip/claim much, keep closer to opponent to counterclaim
        if (nx, ny) not in unclaimed and (nx, ny) not in opp_terr:
            val -= 15 * (dist_opp)

        if val > best_val:
            best_val = val
            best = (dx, dy)

    return [int(best[0]), int(best[1])]