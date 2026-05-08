def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    pos = observation.get("self_position") or [0, 0]
    sx, sy = int(pos[0]), int(pos[1])
    opp = observation.get("opponent_position") or [0, 0]
    ox, oy = int(opp[0]), int(opp[1])

    obstacles = set(map(tuple, observation.get("obstacles") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    dirs = [(-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1), (0, 0)]
    opppt = (ox, oy)

    best_move = (0, 0)
    best_score = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        if (nx, ny) in unclaimed:
            dist_unclaimed = 0
        else:
            dist_unclaimed = 10**9
            if unclaimed:
                for ux, uy in unclaimed:
                    d = abs(nx - ux) + abs(ny - uy)
                    if d < dist_unclaimed:
                        dist_unclaimed = d

        dist_op = man((nx, ny), opppt)
        score = (-dist_unclaimed) + 0.12 * dist_op

        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]