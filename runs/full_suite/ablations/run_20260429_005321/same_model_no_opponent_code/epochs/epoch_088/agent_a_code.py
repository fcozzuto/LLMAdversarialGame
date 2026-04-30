def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def clamp(x, y):
        if x < 0: x = 0
        elif x >= w: x = w - 1
        if y < 0: y = 0
        elif y >= h: y = h - 1
        return x, y

    # Choose a deterministic target: maximize (opp_dist - our_dist), tie-break by distance and parity.
    if resources:
        best = None
        best_adv = None
        best_d = None
        for r in sorted(resources):
            rx, ry = r
            ourd = man(sx, sy, rx, ry)
            oppd = man(ox, oy, rx, ry)
            adv = oppd - ourd
            d = ourd
            if best is None:
                best, best_adv, best_d = r, adv, d
            else:
                if adv > best_adv:
                    best, best_adv, best_d = r, adv, d
                elif adv == best_adv:
                    if d < best_d or (d == best_d and ((rx + ry) & 1) == (observation.get("turn_index", 0) & 1)):
                        best, best_adv, best_d = r, adv, d
        tx, ty = best
    else:
        # No visible resources: move to a safe "race line" toward far corner while avoiding obstacles.
        tx, ty = (w - 1, 0) if ((observation.get("turn_index", 0) & 1) == 0) else (0, h - 1)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    candidates = []
    for dx, dy in deltas:
        nx, ny = clamp(sx + dx, sy + dy)
        if (nx, ny) in obstacles:
            continue
        ourd = man(nx, ny, tx, ty)
        oppd = man(ox, oy, tx, ty)
        adv = oppd - ourd
        candidates.append((adv, ourd, abs(nx - tx) + abs(ny - ty), dx, dy))
    if not candidates:
        for dx, dy in deltas:
            nx, ny = clamp(sx + dx, sy + dy)
            ourd = man(nx, ny, tx, ty)
            oppd = man(ox, oy, tx, ty)
            adv = oppd - ourd
            candidates.append((adv, ourd, abs(nx - tx) + abs(ny - ty), dx, dy))

    candidates.sort(key=lambda t: (-t[0], t[1], t[2], t[3], t[4]))
    return [int(candidates[0][3]), int(candidates[0][4])]