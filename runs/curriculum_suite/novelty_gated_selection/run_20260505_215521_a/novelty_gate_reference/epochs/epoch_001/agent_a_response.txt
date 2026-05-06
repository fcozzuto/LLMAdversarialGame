def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    resources = observation.get("resources", [])
    if resources:
        tx, ty = None, None
        bestd = None
        for rx, ry in resources:
            d = max(abs(rx - sx), abs(ry - sy))
            if bestd is None or d < bestd or (d == bestd and (rx < tx or (rx == tx and ry < ty))):
                bestd = d
                tx, ty = rx, ry
    else:
        tx, ty = w // 2, h // 2

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # Deterministic tie-break order: earlier in deltas list wins.
    best = None
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        dist = max(abs(tx - nx), abs(ty - ny))
        oppdist = max(abs(ox - nx), abs(oy - ny))
        # Prefer reaching target; mildly discourage giving opponent closer access to same target.
        score = dist * 100 + (0 if (nx, ny) == (tx, ty) else 1) * 0 + (-oppdist)
        if best_score is None or score < best_score:
            best_score = score
            best = [dx, dy]

    if best is not None:
        return best
    # If all legal moves blocked/out of bounds, stay.
    return [0, 0]