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

    unclaimed = set()
    for p in observation.get("unclaimed_cells") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                unclaimed.add((x, y))

    resources = set()
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                resources.add((x, y))

    def dist(a, b, c, d):
        dx, dy = a - c, b - d
        return (dx if dx >= 0 else -dx) + (dy if dy >= 0 else -dy)

    dirs = [(1, 0), (-1, 0), (0, 1), (0, -1), (0, 0)]
    cx, cy = w // 2, h // 2
    best = None
    bestv = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        v = 0
        if (nx, ny) in resources:
            v += 1000
        if (nx, ny) in unclaimed:
            v += 200
        v += -dist(nx, ny, cx, cy) // 2
        v += dist(nx, ny, ox, oy) * 3
        v += -dist(nx, ny, sx, sy)  # discourage unnecessary moves (keeps deterministic tie-breaking)
        if best is None or v > bestv:
            best, bestv = [dx, dy], v
        elif v == bestv and best is not None:
            if [dx, dy] < best:
                best = [dx, dy]
    if best is None:
        return [0, 0]
    return best