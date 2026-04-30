def choose_move(observation):
    sx, sy = observation["self_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    obstacles = observation.get("obstacles", []) or []
    obs = {(p[0], p[1]) for p in obstacles}

    resources = observation.get("resources", []) or []
    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    # Pick nearest resource by Manhattan distance
    target = None
    bestd = 10**9
    for rx, ry in resources:
        d = abs(rx - sx) + abs(ry - sy)
        if d < bestd:
            bestd = d
            target = (rx, ry)
    tx, ty = target

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # Prefer moves that reduce distance to target while avoiding obstacles; tie-break deterministically by dx,dy order
    scored = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        dist = abs(tx - nx) + abs(ty - ny)
        scored.append((dist, abs(tx - nx), abs(ty - ny), dx, dy))
    if scored:
        scored.sort()
        return [scored[0][3], scored[0][4]]

    # If all adjacent are blocked (should be rare), stay put
    return [0, 0]