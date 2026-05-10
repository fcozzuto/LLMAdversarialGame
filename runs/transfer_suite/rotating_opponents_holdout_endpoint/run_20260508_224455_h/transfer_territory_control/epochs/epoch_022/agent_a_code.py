def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = int(observation.get("grid_width", 0))
    h = int(observation.get("grid_height", 0))
    obstacles = set(map(tuple, observation.get("obstacles", [])) or [])
    unclaimed = set(map(tuple, observation.get("unclaimed_cells", []) or []))

    dirs = [(0, 1), (1, 0), (0, -1), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1), (0, 0)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    best = None
    best_sc = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        if (nx, ny) == (ox, oy):
            continue
        sc = 0
        if (nx, ny) in unclaimed:
            sc += 1000
        sc -= abs(nx - ox) + abs(ny - oy)
        if dx == 0 and dy == 0:
            sc -= 1
        if sc > best_sc:
            best_sc = sc
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]