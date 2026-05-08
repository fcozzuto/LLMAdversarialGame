def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    obstacles = set(observation.get("obstacles", []))
    unclaimed = set(observation.get("unclaimed_cells", []))
    resources = set(observation.get("resources", []))
    opp_cells = set(observation.get("opponent_territory", []))
    self_cells = set(observation.get("self_territory", []))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    best = None
    best_key = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        if (nx, ny) == (ox, oy):
            continue

        d = cheb(nx, ny, ox, oy)

        # Heuristic: move toward opponent, then toward contestable/unclaimed/resource cells.
        key = (-(10 * d) + (3 if (nx, ny) in opp_cells else 0) + (6 if (nx, ny) in resources else 0) +
               (4 if (nx, ny) in unclaimed else 0) - (2 if (nx, ny) in self_cells else 0),
               -nx, -ny)

        if best_key is None or key > best_key:
            best_key = key
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best