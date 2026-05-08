def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    px, py = observation.get("opponent_position", (0, 0))
    sx, sy, px, py = int(sx), int(sy), int(px), int(py)

    obs_list = observation.get("obstacles") or []
    blocked = set()
    for p in obs_list:
        x, y = int(p[0]), int(p[1])
        if 0 <= x < w and 0 <= y < h:
            blocked.add((x, y))

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    best = None
    best_key = None

    # Prefer moving toward opponent; tie-break deterministically.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in blocked:
            continue
        d = abs(nx - px) + abs(ny - py)
        d0 = abs(sx - px) + abs(sy - py)
        moved = 1 if (dx != 0 or dy != 0) else 0
        key = (d, -moved, abs(dx), abs(dy), dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best