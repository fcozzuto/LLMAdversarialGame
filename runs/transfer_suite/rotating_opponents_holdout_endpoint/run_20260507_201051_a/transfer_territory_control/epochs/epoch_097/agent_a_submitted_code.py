def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (w - 1, h - 1)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obst = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    targets = []
    for c in observation.get("unclaimed_cells") or []:
        if isinstance(c, (list, tuple)) and len(c) >= 2:
            x, y = int(c[0]), int(c[1])
            if inb(x, y):
                edge = 1 if (x == 0 or x == w - 1 or y == 0 or y == h - 1) else 0
                targets.append((edge, abs(x - sx) + abs(y - sy), x, y))
    targets.sort()
    if targets:
        _, _, tx, ty = targets[0]
    else:
        tx, ty = ox, oy  # if nothing known, drift deterministically toward opponent side

    best = (10**18, None)
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            d = abs(nx - tx) + abs(ny - ty)
            # tie-break deterministically: closer to target, then farther from opponent, then lexicographic move
            key = (d, -(abs(nx - ox) + abs(ny - oy)), dx, dy)
            if key < best:
                best = (key, (dx, dy))
    return best[1] if best[1] is not None else [0, 0]