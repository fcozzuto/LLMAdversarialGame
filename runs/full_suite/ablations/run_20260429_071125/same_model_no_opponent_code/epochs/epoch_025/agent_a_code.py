def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    x, y = observation.get("self_position", [0, 0])[:2]
    ox, oy = observation.get("opponent_position", [0, 0])[:2]
    x, y, ox, oy = int(x), int(y), int(ox), int(oy)

    occ = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            px, py = int(p[0]), int(p[1])
            if 0 <= px < w and 0 <= py < h:
                occ.add((px, py))

    resources = []
    for p in observation.get("resources", []) or []:
        if p and len(p) >= 2:
            rx, ry = int(p[0]), int(p[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in occ:
                resources.append((rx, ry))

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in occ

    def best_resource_dist(nx, ny):
        if not resources:
            return 10**9
        best = 10**9
        for rx, ry in resources:
            d = man(nx, ny, rx, ry)
            if d < best:
                best = d
        return best

    best = None
    best_val = 10**18
    for dx, dy in deltas:
        nx, ny = x + dx, y + dy
        if not valid(nx, ny):
            continue
        if resources:
            val = best_resource_dist(nx, ny)
        else:
            val = man(nx, ny, ox, oy)
        if val < best_val:
            best_val = val
            best = [dx, dy]

    return best if best is not None else [0, 0]