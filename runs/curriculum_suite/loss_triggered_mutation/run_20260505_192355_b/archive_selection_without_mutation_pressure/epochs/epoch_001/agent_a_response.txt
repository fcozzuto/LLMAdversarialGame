def choose_move(observation):
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((p[0], p[1]) for p in observation.get("obstacles", []))
    resources = [(p[0], p[1]) for p in observation.get("resources", [])]
    if not resources:
        return [0, 0]

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def dist(a, b, c, d):
        return abs(a-c) + abs(b-d)

    def best_target():
        best = None
        for rx, ry in resources:
            ds = dist(x, y, rx, ry)
            do = dist(ox, oy, rx, ry)
            # Prefer winning races (ds <= do), then maximize (do-ds), then minimize ds, then deterministic tie.
            race = 1 if ds <= do else 0
            score = (race, do - ds, -ds, -rx, -ry)
            if best is None or score > best[0]:
                best = (score, (rx, ry))
        return best[1]

    tx, ty = best_target()
    # Compute candidate move: step that reduces distance to target and is not blocked.
    current_d = dist(x, y, tx, ty)
    cand = []
    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if 0 <= nx < observation["grid_width"] and 0 <= ny < observation["grid_height"] and (nx, ny) not in obstacles:
            nd = dist(nx, ny, tx, ty)
            # prefer closer, then deterministic order via tuple
            cand.append((-(nd < current_d), -nd, dx, dy, nx, ny))
    if cand:
        cand.sort()
        # smallest tuple after sort: but we want closer => nd smaller. Use direct sort key by (better, nd, tie)
        bestm = None
        bestkey = None
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if 0 <= nx < observation["grid_width"] and 0 <= ny < observation["grid_height"] and (nx, ny) not in obstacles:
                nd = dist(nx, ny, tx, ty)
                key = (nd, (dx, dy))
                if bestkey is None or key < bestkey:
                    bestkey = key
                    bestm = (dx, dy)
        return [int(bestm[0]), int(bestm[1])]

    # If all adjacent are blocked, try staying; otherwise pick first legal.
    if (x, y) not in obstacles:
        return [0, 0]
    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if 0 <= nx < observation["grid_width"] and 0 <= ny < observation["grid_height"] and (nx, ny) not in obstacles:
            return [int(dx), int(dy)]
    return [0, 0]