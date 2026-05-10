def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (sx, sy))
    w = int(observation.get("grid_width", 1))
    h = int(observation.get("grid_height", 1))
    obstacles = observation.get("obstacles") or []
    obst = {(p[0], p[1]) for p in obstacles if isinstance(p, (list, tuple)) and len(p) >= 2}
    rx = observation.get("resources") or []
    remaining = observation.get("remaining_resource_count", len(rx) if rx else 0)
    if remaining and rx:
        targets = [(p[0], p[1]) for p in rx if isinstance(p, (list, tuple)) and len(p) >= 2]
        tx, ty = min(targets, key=lambda t: abs(t[0] - sx) + abs(t[1] - sy))
    else:
        tx, ty = ox, oy

    best = None
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                nx, ny = sx, sy
            else:
                nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h):
                continue
            if (nx, ny) in obst:
                continue
            d = abs(tx - nx) + abs(ty - ny)
            score = (d, abs(ox - nx) + abs(oy - ny))
            cand = (score, dx, dy)
            if best is None or cand < best:
                best = cand
    if best is None:
        return [0, 0]
    return [best[1], best[2]]