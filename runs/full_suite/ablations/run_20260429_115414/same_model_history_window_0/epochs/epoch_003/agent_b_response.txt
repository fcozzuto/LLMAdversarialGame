def choose_move(observation):
    w = observation.get('grid_width', 8)
    h = observation.get('grid_height', 8)
    sx, sy = observation.get('self_position', [0, 0])
    ox, oy = observation.get('opponent_position', [0, 0])
    resources = observation.get('resources', [])
    obstacles = set(tuple(p) for p in observation.get('obstacles', []))

    if not resources:
        return [0, 0]

    def dist(a, b):
        return (a[0] - b[0]) * (a[0] - b[0]) + (a[1] - b[1]) * (a[1] - b[1])

    best = None
    best_key = None
    for r in resources:
        rx, ry = r
        d_self = dist((sx, sy), (rx, ry))
        d_opp = dist((ox, oy), (rx, ry))
        # Prefer resources where we're closer; tie-break deterministically by coordinates
        key = (d_opp - d_self, -d_self, -rx, -ry)
        if best is None or key > best_key:
            best = (rx, ry)
            best_key = key

    tx, ty = best
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    # Deterministic ordering: prefer decreasing distance, then fixed move order by dx,dy
    scored = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        scored.append(((dist((nx, ny), (tx, ty))), dx, dy, nx, ny))
    if not scored:
        return [0, 0]
    scored.sort(key=lambda t: (t[0], t[1], t[2]))
    _, dx, dy, _, _ = scored[0]
    return [int(dx), int(dy)]