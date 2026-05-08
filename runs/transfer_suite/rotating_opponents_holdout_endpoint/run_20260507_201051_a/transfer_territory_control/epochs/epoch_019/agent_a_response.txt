def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])

    obstacles = set(map(tuple, observation.get("obstacles") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))
    st = set(map(tuple, observation.get("self_territory") or []))
    ot = set(map(tuple, observation.get("opponent_territory") or []))

    cx, cy = w // 2, h // 2
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    best_move = (0, 0)
    best_val = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue

        # Heuristic: prioritize flipping opponent territory, then capturing unclaimed near center,
        # while staying away from opponent when possible.
        if (nx, ny) in ot:
            val = 120
        elif (nx, ny) in unclaimed:
            val = 70 - (abs(nx - cx) + abs(ny - cy)) + 2 * (abs(nx - ox) + abs(ny - oy) < 6)
        elif (nx, ny) in st:
            val = 30
        else:
            val = 10

        # Encourage progressing toward the best "cut" directions: reduce distance to center,
        # but also create distance from opponent unless we are flipping.
        val += -2 * (abs(nx - cx) + abs(ny - cy))
        if (nx, ny) not in ot:
            val += 3 * (abs(nx - ox) + abs(ny - oy))

        # Deterministic tie-break: fixed dir order above and then lexicographic dx,dy
        if best_val is None or val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]