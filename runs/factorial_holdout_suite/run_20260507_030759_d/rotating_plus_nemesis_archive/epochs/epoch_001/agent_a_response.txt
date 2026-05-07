def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    # If no resources, just stay
    if not resources:
        return [0, 0]

    # Pick nearest resource deterministically (Chebyshev distance for diagonal moves)
    def dist_key(p):
        x, y = p
        d = max(abs(x - sx), abs(y - sy))
        return (d, abs(x - ox) - abs(y - oy), x, y)

    target = sorted(resources, key=dist_key)[0]
    tx, ty = target

    # Move one step toward target (diagonal allowed). Avoid stepping onto obstacles.
    dx0 = 0 if tx == sx else (1 if tx > sx else -1)
    dy0 = 0 if ty == sy else (1 if ty > sy else -1)

    candidates = []
    candidates.append((dx0, dy0))
    candidates.append((dx0, 0))
    candidates.append((0, dy0))
    candidates.append((dx0, -dy0))
    candidates.append((-dx0, dy0))
    candidates.append((0, 0))

    # Deterministically break ties by ordering candidates
    cand_order = []
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            # Prefer moves that reduce distance to target
            nd = max(abs(tx - nx), abs(ty - ny))
            cand_order.append((nd, nx, ny, dx, dy))

    if not cand_order:
        return [0, 0]
    nd, nx, ny, dx, dy = sorted(cand_order, key=lambda t: (t[0], t[1], t[2], t[3], t[4]))[0]
    return [dx, dy]