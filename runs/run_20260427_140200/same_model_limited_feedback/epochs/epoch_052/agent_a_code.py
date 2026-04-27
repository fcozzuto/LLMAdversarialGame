def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    # Candidate moves in deterministic preference order
    moves = [[0, 0], [1, 0], [-1, 0], [0, 1], [0, -1], [1, 1], [1, -1], [-1, 1], [-1, -1]]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def dist_to_best(x, y):
        best = None
        for rx, ry in resources:
            ds = man(x, y, rx, ry)
            do = man(ox, oy, rx, ry)
            # Prefer resources where we are closer than opponent
            val = (10.0 / (ds + 1)) - (8.0 / (do + 1))
            if best is None or val > best[0]:
                best = (val, rx, ry, ds, do)
        return best

    best_move = [0, 0]
    best_val = -1e18

    current_best = dist_to_best(sx, sy)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        if (nx, ny) in obstacles:
            val = -1e9
        else:
            nxt_best = dist_to_best(nx, ny)
            if nxt_best is None:
                val = 0
            else:
                tv, rx, ry, ds, do = nxt_best
                # Immediate resource pick incentive
                if (nx, ny) in obstacles:
                    val = -1e9
                else:
                    val = tv
                    if (nx, ny) == (rx, ry):
                        val += 50.0
                    # Discourage stepping into opponent's immediate reach
                    if (man(nx, ny, ox, oy) <= 1):
                        val -= 2.5
                    # Slight preference to move toward the chosen best target of current state
                    if current_best is not None:
                        _, crx, cry, _, _ = current_best
                        val += 0.2 * (man(sx, sy, crx, cry) - man(nx, ny, crx, cry))
        if val > best_val:
            best_val = val
            best_move = [dx, dy]
    return [int(best_move[0]), int(best_move[1])]