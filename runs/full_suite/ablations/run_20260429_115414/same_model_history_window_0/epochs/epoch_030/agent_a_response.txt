def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obst = set((x, y) for x, y in obstacles)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    if not resources:
        dx = 1 if sx <= w // 2 else -1 if sx > w // 2 else 0
        dy = 1 if sy <= h // 2 else -1 if sy > h // 2 else 0
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obst:
            return [dx, dy]
        return [0, 0]

    best = None
    best_key = None
    for rx, ry in resources:
        sd = dist((sx, sy), (rx, ry))
        od = dist((ox, oy), (rx, ry))
        # Prefer resources where we're at least as close as opponent; break ties by being closer to them.
        key = (od - sd, -sd, -(abs(rx - ox) + abs(ry - oy)))
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)
    tx, ty = best

    deltas = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obst:
                deltas.append((dx, dy))

    if not deltas:
        return [0, 0]

    best_move = None
    best_move_key = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        td = dist((nx, ny), (tx, ty))
        od = dist((nx, ny), (ox, oy))
        # Minimize distance to target; tie-break by keeping distance from opponent.
        key = (td, -od)
        if best_move_key is None or key < best_move_key:
            best_move_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]