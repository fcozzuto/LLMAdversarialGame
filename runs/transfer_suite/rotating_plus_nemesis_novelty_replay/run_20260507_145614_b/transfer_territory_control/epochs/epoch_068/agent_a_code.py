def choose_move(observation):
    w = observation.get("grid_width", 0)
    h = observation.get("grid_height", 0)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = p[0], p[1]
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    res = observation.get("resources") or []
    resources = []
    for p in res:
        if p and len(p) >= 2:
            x, y = p[0], p[1]
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    best = [0, 0]
    bestv = -10**18
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h):
                continue
            if (nx, ny) in obstacles:
                continue
            dfo = man(nx, ny, ox, oy)  # prefer away
            if resources:
                dfr = min(man(nx, ny, rx, ry) for rx, ry in resources)  # prefer closer to resource
                v = dfo * 100 - dfr
            else:
                v = dfo
            if v > bestv:
                bestv = v
                best = [dx, dy]

    if best == [0, 0]:
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = sx + dx, sy + dy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                    return [dx, dy]
        return [0, 0]
    return best