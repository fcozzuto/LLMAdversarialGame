def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))

    rolestr = (observation.get("self_role") or "").lower()
    is_evader = ("evad" in rolestr)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    if is_evader:
        # Prefer the corner that increases distance from the pursuer
        best_corner = max(corners, key=lambda c: (c[0] - ox) ** 2 + (c[1] - oy) ** 2)
    else:
        # Prefer the corner that reduces distance to the evader (to corner them)
        best_corner = min(corners, key=lambda c: (c[0] - ox) ** 2 + (c[1] - oy) ** 2)

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    # Deterministic tie-break: fixed order by deltas, no randomness
    best_move = (0, 0)
    best_score = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        d2 = (nx - ox) ** 2 + (ny - oy) ** 2
        # Corner pressure: move in the direction of chosen corner
        corner_dx = 0 if best_corner[0] == nx else (1 if best_corner[0] > nx else -1)
        corner_dy = 0 if best_corner[1] == ny else (1 if best_corner[1] > ny else -1)
        align = (dx == corner_dx) + (dy == corner_dy)  # 0..2

        # Small obstacle-field term: prefer positions with more free neighboring cells
        free_neighbors = 0
        for adx, ady in deltas:
            tx, ty = nx + adx, ny + ady
            if valid(tx, ty):
                free_neighbors += 1

        if is_evader:
            score = d2 * 4.0 + align * 2.0 + free_neighbors * 0.05
            if best_score is None or score > best_score:
                best_score = score
                best_move = (dx, dy)
        else:
            score = -d2 * 4.0 + align * 2.0 + free_neighbors * 0.05
            if best_score is None or score > best_score:
                best_score = score
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]