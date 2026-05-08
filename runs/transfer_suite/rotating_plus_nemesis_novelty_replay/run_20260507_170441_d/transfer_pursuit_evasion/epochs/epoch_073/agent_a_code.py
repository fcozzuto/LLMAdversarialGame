def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for o in (observation.get("obstacles", []) or []):
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            x, y = int(o[0]), int(o[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    role = (observation.get("self_role", "") or "").lower()
    evader = ("evader" in role) or ("runner" in role)

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]
    best_move = (0, 0)
    best_val = -10**18 if evader else 10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        dist = abs(nx - ox) + abs(ny - oy)
        if evader:
            val = dist
            if val > best_val or (val == best_val and (dx, dy) < best_move):
                best_val, best_move = val, (dx, dy)
        else:
            val = -dist
            if val > best_val or (val == best_val and (dx, dy) < best_move):
                best_val, best_move = val, (dx, dy)

    return [int(best_move[0]), int(best_move[1])]