def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        for p in observation.get("unclaimed_cells") or []:
            if p and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                    resources.append((x, y))

    def best_score(nx, ny):
        if (nx, ny) in obstacles or not (0 <= nx < w and 0 <= ny < h):
            return -10**9
        if resources:
            d0 = min((abs(nx - rx) + abs(ny - ry)) for rx, ry in resources)
        else:
            d0 = abs(nx - ox) + abs(ny - oy)
        d1 = abs(nx - ox) + abs(ny - oy)
        return -d0 * 10 - d1  # deterministic: prefer closer to resources, then farther from opponent

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = (-10**18, 0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        sc = best_score(nx, ny)
        if sc > best[0]:
            best = (sc, dx, dy)
    dx, dy = best[1], best[2]
    if dx not in (-1, 0, 1) or dy not in (-1, 0, 1):
        dx, dy = 0, 0
    return [int(dx), int(dy)]