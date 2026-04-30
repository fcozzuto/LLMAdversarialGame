def choose_move(observation):
    w = observation.get('grid_width', 8)
    h = observation.get('grid_height', 8)
    sx, sy = observation['self_position']
    ox, oy = observation['opponent_position']
    resources = observation.get('resources', []) or []
    obstacles = observation.get('obstacles', []) or []

    if not resources:
        return [0, 0]

    obs_set = set((x, y) for x, y in obstacles)
    valid = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs_set:
                valid.append((dx, dy, nx, ny))

    def dist2(a, b, c, d):
        dx = a - c
        dy = b - d
        return dx * dx + dy * dy

    best_target = None
    best_gap = None
    best_selfd = None
    for rx, ry in resources:
        if (rx, ry) in obs_set:
            continue
        sd = dist2(sx, sy, rx, ry)
        od = dist2(ox, oy, rx, ry)
        gap = od - sd
        if best_target is None:
            best_target, best_gap, best_selfd = (rx, ry), gap, sd
        else:
            if gap > best_gap or (gap == best_gap and sd < best_selfd):
                best_target, best_gap, best_selfd = (rx, ry), gap, sd

    if best_gap is None or best_gap < 0:
        rx, ry = min(resources, key=lambda p: dist2(sx, sy, p[0], p[1]))
        best_target = (rx, ry)

    tx, ty = best_target
    best_move = (0, 0, sx, sy)
    best_score = None
    for dx, dy, nx, ny in valid:
        nd_self = dist2(nx, ny, tx, ty)
        nd_opp = dist2(nx, ny, ox, oy)
        # Prefer smaller distance to target; if tie, keep away from opponent; then reduce step
        step = abs(dx) + abs(dy)
        score = (nd_self, -nd_opp, step)
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy, nx, ny)

    return [best_move[0], best_move[1]]