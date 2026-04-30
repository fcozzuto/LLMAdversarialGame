def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def dist(a, b):
        return max(abs(a[0]-b[0]), abs(a[1]-b[1]))  # Chebyshev for 8-neigh

    # If no resources, head to center
    if not resources:
        tx, ty = (w-1)//2, (h-1)//2
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        return [dx, dy]

    # Choose target resource by being earlier than opponent; if tied, prefer closer to self
    best = None
    best_key = None
    for rx, ry in resources:
        dS = dist((sx, sy), (rx, ry))
        dO = dist((ox, oy), (rx, ry))
        # Key: prioritize large lead, then closeness, then bottom-right bias for determinism
        lead = dO - dS
        key = (lead, -dS, rx, ry)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best
    # Candidate moves (including stay), deterministic order
    cand = []
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                cand.append((dx, dy))

    # Score candidates: prefer reducing distance to target; also discourage moving into opponent reach
    best_move = (0, 0)
    best_score = None
    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        dT = dist((nx, ny), (tx, ty))
        dO = dist((nx, ny), (ox, oy))
        # Being closer to target is primary; being too close to opponent is a secondary penalty
        score = (-dT, dO, dx, dy)
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]