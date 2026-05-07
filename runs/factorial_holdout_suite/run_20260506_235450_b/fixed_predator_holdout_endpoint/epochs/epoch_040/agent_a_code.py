def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    if not resources:
        return [0, 0]
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    res = [(int(r[0]), int(r[1])) for r in resources]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_val = -10**30

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue

        sd_min = 10**9
        od_min = 10**9
        val = 0

        for rx, ry in res:
            sd = abs(nx - rx) + abs(ny - ry)
            od = abs(ox - rx) + abs(oy - ry)
            if sd < sd_min:
                sd_min = sd
            if od < od_min:
                od_min = od

            if sd == 0:
                val += 10**7
            else:
                # If opponent can reach this resource sooner, heavily penalize.
                if od < sd:
                    val -= (sd - od) * 500
                # If I can reach sooner, reward and slightly encourage closeness.
                elif sd < od:
                    val += (od - sd) * 200
                # Mild preference for overall closer resources.
                val -= sd

        # Global differential based on closest resource I vs opponent.
        val += (od_min - sd_min) * 120

        # Tiny deterministic tie-break by preferring straight moves over diagonals, then staying.
        if dx != 0 and dy != 0:
            val -= 3
        if dx == 0 and dy == 0:
            val -= 1

        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]