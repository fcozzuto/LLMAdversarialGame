def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Choose a target resource: prefer one we can reach sooner than opponent.
    best_t = None
    best_key = None
    for r in resources:
        rt = tuple(r)
        d_self = dist((sx, sy), rt)
        d_opp = dist((ox, oy), rt)
        # Key: maximize advantage, then prefer closer.
        key = (d_opp - d_self, -d_self, rt[0], rt[1])
        if best_key is None or key > best_key:
            best_key = key
            best_t = rt

    # If no resources, head to center.
    if best_t is None:
        best_t = (w // 2, h // 2)

    tx, ty = best_t

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    best_move = (0, 0)
    best_score = None

    # Deterministic tie-break order by dx,dy already fixed in list.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        d = dist((nx, ny), (tx, ty))
        # Avoid moving into opponent vicinity.
        opp_d = dist((nx, ny), (ox, oy))
        # Score: prioritize smaller distance to target, then larger distance from opponent.
        score = (-d, opp_d, -abs(dx) - abs(dy), dx, dy)
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    # If all moves invalid (surrounded), stay.
    return [int(best_move[0]), int(best_move[1])]