def choose_move(observation):
    w = observation.get("grid_width", 0)
    h = observation.get("grid_height", 0)
    sp = observation.get("self_position", (0, 0))
    op = observation.get("opponent_position", None) or sp
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    bestd = 10**9

    # Heuristic: chase opponent; if moving would hit obstacle, avoid it.
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs:
            continue
        d = abs(nx - ox) + abs(ny - oy)
        if d < bestd:
            bestd = d
            best = (dx, dy)

    if best is not None:
        return [best[0], best[1]]

    # Fallback: move to any non-obstacle in-bounds, else stay.
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
            return [dx, dy]
    return [0, 0]