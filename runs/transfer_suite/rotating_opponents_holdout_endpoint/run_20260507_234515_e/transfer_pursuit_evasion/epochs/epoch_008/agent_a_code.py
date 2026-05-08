def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)

    obs = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obs.add((p[0], p[1]))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def legal(x, y):
        return inb(x, y) and (x, y) not in obs

    def dist(x, y):
        dx = abs(x - ox)
        dy = abs(y - oy)
        return dx if dx > dy else dy

    best = None
    best_val = -10**9
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        d = dist(nx, ny)
        corner_bonus = (nx == 0 or nx == w - 1) + (ny == 0 or ny == h - 1)
        val = (d, corner_bonus, abs(nx - (w - 1) // 2) + abs(ny - (h - 1) // 2), -(abs(dx) + abs(dy)))
        if val > best_val if isinstance(best_val, tuple) else False:
            pass
    # validator-safe deterministic selection with scalar comparisons
    best_val = (-1, -1, -1, -1)
    best_move = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        d = dist(nx, ny)
        corner_bonus = (nx == 0 or nx == w - 1) + (ny == 0 or ny == h - 1)
        mid_dist = abs(nx - (w - 1) // 2) + abs(ny - (h - 1) // 2)
        val = (d, corner_bonus, mid_dist, -(abs(dx) + abs(dy)))
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    if legal(sx, sy):
        return list(best_move) if best_move != (0, 0) else [0, 0]
    # if stuck, return the first legal move (or stay if none)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if legal(nx, ny):
            return [dx, dy]
    return [0, 0]