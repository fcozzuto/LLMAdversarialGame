def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [7, 7])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources_in = observation.get("resources", []) or []
    obstacles_in = observation.get("obstacles", []) or []
    resources = []
    for p in resources_in:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            resources.append((int(p[0]), int(p[1])))
    obstacles = set()
    for p in obstacles_in:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    if not resources:
        return [0, 0]

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    best_move = (0, 0)
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        # If we land on a resource, it's almost always best.
        landed = any((rx == nx and ry == ny) for rx, ry in resources)
        if landed:
            val = 10**9
        else:
            # Choose move that increases our lead over the opponent on the best remaining resource,
            # and mildly discourages squares close to opponent (shadow-like opponents steal).
            val = -10**9
            opp_pen = - (dist(nx, ny, ox, oy) == 0) * 50 - (dist(nx, ny, ox, oy) <= 2) * 5
            for rx, ry in resources:
                ds = dist(nx, ny, rx, ry)
                do = dist(ox, oy, rx, ry)
                lead = do - ds  # positive means we are closer
                # Favor resources that are reachable soon even if lead is small.
                reach = -ds
                score = 100 * lead + reach + opp_pen
                # Tie-break deterministically: prefer smaller rx, then ry.
                score += -0.0001 * rx - 0.00001 * ry
                if score > val:
                    val = score

        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)
        elif val == best_val:
            # Deterministic tie-break order: lexicographic dx,dy preference towards 0 then +
            if (dx, dy) < best_move:
                best_move = (dx, dy)

    dx, dy = best_move
    return [int(dx), int(dy)]