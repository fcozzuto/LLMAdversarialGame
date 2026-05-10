def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    ob = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            ob.add((int(p[0]), int(p[1])))

    role = (observation.get("self_role") or "").lower()
    is_evader = "evader" in role

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(nx, ny):
        return in_bounds(nx, ny) and (nx, ny) not in ob

    best_move = [0, 0]
    best_score = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        dist = abs(nx - ox) + abs(ny - oy)
        # Add slight bias to progress along main axis to avoid dithering.
        axis = abs(nx - sx) + abs(ny - sy)
        if is_evader:
            # Maximize distance; in ties, prefer larger movement away (axis).
            score = (dist, axis, dx, dy)
            if best_score is None or score > best_score:
                best_score = score
                best_move = [dx, dy]
        else:
            # Minimize distance; in ties, prefer larger movement (axis) to commit.
            score = (-dist, axis, -dx, -dy)
            if best_score is None or score > best_score:
                best_score = score
                best_move = [dx, dy]

    if not valid(sx, sy):
        # Rare: if current tile is considered invalid (shouldn't happen), pick first valid neighbor.
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                return [dx, dy]
        return [0, 0]

    return [int(best_move[0]), int(best_move[1])]