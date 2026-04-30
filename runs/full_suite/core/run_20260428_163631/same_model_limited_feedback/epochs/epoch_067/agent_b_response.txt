def choose_move(observation):
    w = observation.get('grid_width', 8)
    h = observation.get('grid_height', 8)
    sx, sy = observation['self_position']
    ox, oy = observation['opponent_position']
    resources = observation.get('resources', [])
    obstacles = set(tuple(p) for p in observation.get('obstacles', []))

    def cheb(a, b, c, d):
        return max(abs(a - c), abs(b - d))

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                val = -cheb(nx, ny, tx, ty)
                if best is None or val > best[0]:
                    best = (val, [dx, dy])
        return best[1] if best else [0, 0]

    best_move = [0, 0]
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        # Lower is better: minimize (self_dist - opp_dist) to a resource, ties broken by self_dist
        best_adv = None
        best_self = None
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            adv = ds - do
            if best_adv is None or adv < best_adv or (adv == best_adv and ds < best_self):
                best_adv, best_self = adv, ds
        # Small bias to progress: prefer smaller self distance when advantage equal
        val = (best_adv, best_self)
        if best_val is None or val < best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move if best_move is not None else [0, 0]