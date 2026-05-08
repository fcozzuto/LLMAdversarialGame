def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    self_role = (observation.get("self_role") or "").lower()
    is_pursuer = "pursuer" in self_role

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def legal(x, y):
        return in_bounds(x, y) and (x, y) not in obstacles

    def escape_potential(x, y, depth=4):
        # Maximize distance-to-opponent reachable within depth, ignoring opponent/capture.
        best = 0
        frontier = [(x, y, 0)]
        seen = set([(x, y)])
        for px, py, d in frontier:
            dist = abs(ox - px) + abs(oy - py)
            if dist > best:
                best = dist
            if d == depth:
                continue
            nd = d + 1
            for dx, dy in moves:
                nx, ny = px + dx, py + dy
                if (nx, ny) not in seen and legal(nx, ny):
                    seen.add((nx, ny))
                    frontier.append((nx, ny, nd))
        return best

    def opp_threat(x, y):
        # "Contact pressure": how many legal next squares for opponent are closer than current.
        closer = 0
        curd = abs(ox - x) + abs(oy - y)
        for dx, dy in moves:
            nx, ny = ox + dx, oy + dy
            if legal(nx, ny):
                if abs(nx - x) + abs(ny - y) < curd:
                    closer += 1
        return closer

    best_move = (0, 0)
    best_score = None
    # Deterministic move ordering tie-breaker
    move_order = sorted(moves)

    for dx, dy in move_order:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue

        dman = abs(ox - nx) + abs(oy - ny)
        pot = escape_potential(nx, ny, depth=4)
        pressure = opp_threat(nx, ny)

        if is_pursuer:
            # Prefer shortest chase; avoid giving evader strong escape.
            score = (-dman * 1000) + (pot * -5) + (-pressure * 3)
            if best_score is None or score > best_score:
                best_score = score
                best_move = (dx, dy)
        else:
            # Evader: maximize distance and escape reach; avoid squares that increase opponent pressure.
            score = (dman * 1000) + (pot * 25) + (-pressure * 50)
            if best_score is None or score > best_score:
                best_score = score
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]