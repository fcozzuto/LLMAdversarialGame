def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    if resources:
        best = None
        for rx, ry in resources:
            d = (rx - sx) * (rx - sx) + (ry - sy) * (ry - sy)
            key = (d, rx, ry)
            if best is None or key < best[0]:
                best = (key, (rx, ry))
        tx, ty = best[1]
    else:
        tx, ty = ox, oy
    best_move = (10**9, 10**9, 0, 0)
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if nx < 0 or nx >= w or ny < 0 or ny >= h:
                continue
            if (nx, ny) in obstacles:
                continue
            dist_t = (tx - nx) * (tx - nx) + (ty - ny) * (ty - ny)
            dist_o = (ox - nx) * (ox - nx) + (oy - ny) * (oy - ny)
            # Prefer moving toward target; slightly prefer getting closer to opponent only when target is opponent
            toward_opponent = 1 if not resources else 0
            score = (dist_t, -dist_o * toward_opponent)
            key = (score[0], score[1], dx, dy)
            if key < best_move:
                best_move = key
    return [best_move[2], best_move[3]]