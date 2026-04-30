def choose_move(observation):
    w = observation.get('grid_width', 8)
    h = observation.get('grid_height', 8)
    sx, sy = observation['self_position']
    ox, oy = observation['opponent_position']
    resources = observation.get('resources', [])
    obstacles = set(tuple(p) for p in observation.get('obstacles', []))

    opts = [(-1, -1), (-1, 0), (-1, 1),
            (0, -1),  (0, 0),  (0, 1),
            (1, -1),  (1, 0),  (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b, c, d):
        dx = a - c
        dy = b - d
        return (dx * dx + dy * dy)

    # If no resources visible, head toward center (deterministic fallback)
    if not resources:
        tx, ty = w // 2, h // 2
        best = None
        for dx, dy in opts:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            val = -dist(nx, ny, tx, ty) + 0.01 * dist(nx, ny, ox, oy)
            if best is None or val > best[0] or (val == best[0] and (dx, dy) < best[1]):
                best = (val, (dx, dy))
        return list(best[1]) if best else [0, 0]

    # Strategic change: instead of nearest resource, race by minimizing (our_dist - 0.8*opp_dist)
    # while also slightly preferring moves that increase distance from opponent.
    best_val = None
    best_move = (0, 0)
    for dx, dy in opts:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            if dx == 0 and dy == 0:
                nx, ny = sx, sy
            else:
                continue

        best_priority = None
        best_r = None
        for rx, ry in resources:
            p = dist(nx, ny, rx, ry) - 0.8 * dist(ox, oy, rx, ry)
            # Tie-break deterministically by coordinate
            if best_priority is None or p < best_priority or (p == best_priority and (rx, ry) < best_r):
                best_priority = p
                best_r = (rx, ry)

        # Higher is better
        val = -best_priority + 0.02 * dist(nx, ny, ox, oy) - 0.001 * dist(nx, ny, best_r[0], best_r[1])
        if best_val is None or val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]