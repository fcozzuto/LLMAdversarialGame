def choose_move(observation):
    w = observation.get('grid_width', 8)
    h = observation.get('grid_height', 8)
    sx, sy = observation['self_position']
    ox, oy = observation['opponent_position']
    resources = observation.get('resources', [])
    obstacles = set(tuple(p) for p in observation.get('obstacles', []))
    best = [0, 0]
    best_val = -10**18

    def clamp(x, y):
        if x < 0: x = 0
        elif x >= w: x = w - 1
        if y < 0: y = 0
        elif y >= h: y = h - 1
        return x, y

    res_set = set(tuple(p) for p in resources)

    def manh(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx + dy

    def nearest_resource_dist(px, py):
        if not resources:
            return 0
        bd = 10**9
        for rx, ry in resources:
            d = (rx - px) * (rx - px) + (ry - py) * (ry - py)
            if d < bd:
                bd = d
        return bd

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]
    for dx, dy in moves:
        nx, ny = clamp(sx + dx, sy + dy)
        if (nx, ny) in obstacles:
            continue
        val = 0
        if (nx, ny) in res_set:
            val += 10**6
        # Prefer moves that reduce distance to resources and keep away from opponent
        nd = nearest_resource_dist(nx, ny)
        val += -nd
        val += 0.2 * manh(nx, ny, ox, oy)
        # Mild preference for moving toward the densest area of remaining resources along axes
        if resources:
            ax_b = 0
            for rx, ry in resources:
                ax_b += 2 if (rx == nx or ry == ny) else 0
            val += ax_b * 0.01
        if val > best_val:
            best_val = val
            best = [dx, dy]
        # Deterministic tie-break: lexicographic on (dx, dy)
        elif val == best_val and [dx, dy] < best:
            best = [dx, dy]
    return best