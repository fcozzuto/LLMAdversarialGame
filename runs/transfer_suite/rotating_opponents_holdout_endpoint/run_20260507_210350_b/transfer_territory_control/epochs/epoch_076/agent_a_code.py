def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (w - 1, h - 1)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    steps = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]
    dx = 1 if ox > sx else (-1 if ox < sx else 0)
    dy = 1 if oy > sy else (-1 if oy < sy else 0)

    # Prefer moving along the larger separation axis toward the opponent
    if abs(ox - sx) >= abs(oy - sy):
        primary = (dx, 0)
        secondary = (0, dy)
    else:
        primary = (0, dy)
        secondary = (dx, 0)

    candidates = [primary, secondary, (dx, dy), (0, 0)]
    for cdx, cdy in candidates:
        nx, ny = sx + cdx, sy + cdy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            return [cdx, cdy]

    # Fallback: first valid step in fixed order
    for cdx, cdy in steps:
        nx, ny = sx + cdx, sy + cdy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            return [cdx, cdy]

    return [0, 0]