def choose_move(observation):
    w = observation.get('grid_width', 8)
    h = observation.get('grid_height', 8)
    sx, sy = observation['self_position']
    ox, oy = observation['opponent_position']
    resources = observation.get('resources', []) or []
    obstacles = set(tuple(p) for p in (observation.get('obstacles', []) or []))
    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def cheb(a, b, c, d):
        dx = a - c
        dy = b - d
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Pick best resource by advantage over opponent, if any
    best_target = None
    best_adv = None
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        adv = od - sd
        if best_adv is None or adv > best_adv or (adv == best_adv and (sd < cheb(sx, sy, best_target[0], best_target[1]) if best_target else True)):
            best_adv = adv
            best_target = (rx, ry)
        elif best_adv == adv and best_target:
            sd = cheb(sx, sy, rx, ry)
            td = cheb(sx, sy, best_target[0], best_target[1])
            if sd == td and (rx, ry) < best_target:
                best_target = (rx, ry)

    candidates = []
    tx, ty = (best_target if best_target else (sx, sy))
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            if best_target:
                before = cheb(sx, sy, tx, ty)
                after = cheb(nx, ny, tx, ty)
                prog = before - after
                # Prefer moves that get closer; break ties by distancing opponent
                oppd = cheb(nx, ny, ox, oy)
                candidates.append((prog, oppd, -after, nx, ny, dx, dy))
            else:
                oppd = cheb(nx, ny, ox, oy)
                center = -abs(nx - (w - 1) / 2.0) - abs(ny - (h - 1) / 2.0)
                candidates.append((oppd, center, nx, ny, dx, dy))

    if not candidates:
        return [0, 0]

    # If moving toward a target exists, prefer best tuple; otherwise maximize opponent distance
    if best_target:
        candidates.sort(key=lambda t: (t[0], t[1], t[2], -t[3], -t[4]), reverse=True)
        return [int(candidates[0][5]), int(candidates[0][6])]

    candidates.sort(key=lambda t: (t[0], t[1]), reverse=True)
    return [int(candidates[0][4]), int(candidates[0][5])]