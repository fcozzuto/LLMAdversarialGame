def choose_move(observation):
    x, y = observation.get("self_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    obstacles = observation.get("obstacles", []) or []
    obs = set((p[0], p[1]) for p in obstacles if p and len(p) >= 2)
    ox, oy = observation.get("opponent_position", [x, y])
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_sc = -10**9
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obs:
            continue
        d = abs(nx - ox) + abs(ny - oy)
        score = -d
        if dx == 0 and dy == 0:
            score -= 1
        un = set((p[0], p[1]) for p in ((observation.get("unclaimed_cells", []) or [])) if p and len(p) >= 2)
        if (nx, ny) in un:
            score += 2
        rt = set((p[0], p[1]) for p in ((observation.get("resources", []) or [])) if p and len(p) >= 2)
        if (nx, ny) in rt:
            score += 3
        if score > best_sc or (score == best_sc and (dx, dy) < best):
            best_sc = score
            best = (dx, dy)
    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]