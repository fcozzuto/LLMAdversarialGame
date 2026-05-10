def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))
    selfT = set(tuple(p) for p in (observation.get("self_territory") or []))
    oppT = set(tuple(p) for p in (observation.get("opponent_territory") or []))

    if not unclaimed and not oppT:
        return [0, 0]

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    deltas = [(-1, -1), (0, -1), (1, -1),
              (-1, 0),  (0, 0),  (1, 0),
              (-1, 1),  (0, 1),  (1, 1)]

    # Choose a deterministic target among unclaimed cells (prefer closeness + center control)
    tx = ty = None
    if unclaimed:
        best_key = None
        for ux, uy in unclaimed:
            d = abs(ux - x) + abs(uy - y)
            center_bias = abs(ux - cx) + abs(uy - cy)
            key = (d, center_bias, uy, ux)
            if best_key is None or key < best_key:
                best_key = key
                tx, ty = ux, uy
    # If no unclaimed, aim at nearest opponent territory to disrupt/steal
    if tx is None:
        best_key = None
        for ox, oy in oppT:
            d = abs(ox - x) + abs(oy - y)
            key = (d, oy, ox)
            if best_key is None or key < best_key:
                best_key = key
                tx, ty = ox, oy

    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in deltas:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        score = 0.0
        # Territory gain weights
        if (nx, ny) in unclaimed:
            score += 10.0
        elif (nx, ny) in oppT:
            score += 6.0
        elif (nx, ny) in selfT:
            score += 1.0
        else:
            score += 0.2

        # Move toward target
        dist = abs(tx - nx) + abs(ty - ny)
        score += 4.0 / (1.0 + dist)

        # Avoid drifting away when already on territory: small penalty for increasing target distance
        cur_dist = abs(tx - x) + abs(ty - y)
        if dist > cur_dist:
            score -= 0.9 * (dist - cur_dist)

        # Edge pressure (opponent archetype often claims edges): prefer staying off corners unless stealing
        corner = (nx in (0, w - 1) and ny in (0, h - 1))
        if corner and (nx, ny) not in oppT:
            score -= 0.8

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]