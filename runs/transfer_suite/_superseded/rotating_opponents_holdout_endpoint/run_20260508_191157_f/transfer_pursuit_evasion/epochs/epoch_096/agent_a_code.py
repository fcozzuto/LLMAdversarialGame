def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = observation.get("grid_width", 1)
    h = observation.get("grid_height", 1)
    obs_list = observation.get("obstacles") or []
    obstacles = set(tuple(p) for p in obs_list)
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    # Aim to get closer to opponent; deterministic tie-break by move order.
    best_dx, best_dy = 0, 0
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        dist = abs(ox - nx) + abs(oy - ny)
        score = -dist
        if score > best_score:
            best_score = score
            best_dx, best_dy = dx, dy

    # Fallback if all moves blocked (shouldn't happen often).
    if not inb(sx, sy):
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny):
                return [dx, dy]
        return [0, 0]

    return [best_dx, best_dy]