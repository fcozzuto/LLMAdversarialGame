def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))
    unclaimed = observation.get("unclaimed_cells") or []
    if unclaimed:
        tx, ty = min((p[0], p[1]) for p in unclaimed if 0 <= p[0] < w and 0 <= p[1] < h and (p[0], p[1]) not in obstacles), key=lambda p: (abs(p[0] - sx) + abs(p[1] - sy), p[0], p[1])
    else:
        tx, ty = (ox, oy) if (observation.get("scores") or [0, 0])[0] <= (observation.get("scores") or [0, 0])[1] else (w // 2, h // 2)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        d = abs(nx - tx) + abs(ny - ty)
        od = abs(nx - ox) + abs(ny - oy)
        safe = 0
        selfT = set((p[0], p[1]) for p in (observation.get("self_territory") or []))
        if (nx, ny) in selfT:
            safe = -1
        score = (d, -od, -safe, abs(dx) + abs(dy), nx, ny)
        if best is None or score < best[0]:
            best = (score, dx, dy)
    if best is None:
        return [0, 0]
    return [best[1], best[2]]