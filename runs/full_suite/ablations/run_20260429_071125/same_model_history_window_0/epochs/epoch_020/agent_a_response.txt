def choose_move(observation):
    w = observation.get('grid_width', 8)
    h = observation.get('grid_height', 8)
    sx, sy = observation['self_position']
    ox, oy = observation['opponent_position']
    obstacles = set(tuple(p) for p in observation.get('obstacles', []))
    resources = observation.get('resources', [])
    # Chebyshev distance (diagonal allowed)
    def dist(a, b):
        return max(abs(a[0]-b[0]), abs(a[1]-b[1]))
    # Choose resource with best advantage (prefer taking closer than opponent)
    best = None
    for r in resources:
        rx, ry = r
        sd = dist((sx, sy), (rx, ry))
        od = dist((ox, oy), (rx, ry))
        adv = od - sd
        val = (adv, -sd, rx, ry)
        if best is None or val > best[0]:
            best = (val, (rx, ry))
    if best is None:
        return [0, 0]
    tx, ty = best[1]
    # Greedy step toward target among legal deltas (deterministic tie-break)
    deltas = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            deltas.append((dx, dy))
    # include staying as fallback
    candidates = deltas + [(0, 0)]
    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles
    best_move = (0, 0)
    best_score = None
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        nd = dist((nx, ny), (tx, ty))
        # Prefer reducing distance; also slightly prefer moving away from opponent if equal
        no = dist((nx, ny), (ox, oy))
        score = (-nd, no, -abs(dx), -abs(dy), dx, dy)
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)
    dx, dy = best_move
    if not legal(sx + dx, sy + dy):
        return [0, 0]
    return [int(dx), int(dy)]