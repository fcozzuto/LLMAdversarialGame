def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    sx, sy = int(sx), int(sy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    selfT = set(tuple(p) for p in (observation.get("self_territory") or []))
    oppT = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))

    cx, cy = (w - 1) // 2, (h - 1) // 2

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    frontier = []
    for ox, oy in oppT:
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = ox + dx, oy + dy
                if inb(nx, ny) and (nx, ny) in unclaimed and (nx, ny) not in obstacles:
                    frontier.append((nx, ny))
    if not frontier:
        frontier = list(unclaimed)

    if not frontier:
        return [0, 0]

    best_target = None
    best_key = None
    for tx, ty in frontier:
        d1 = abs(tx - sx) + abs(ty - sy)
        d2 = abs(tx - cx) + abs(ty - cy)
        key = (d1, -d2, tx, ty)
        if best_key is None or key < best_key:
            best_key = key
            best_target = (tx, ty)
    tx, ty = best_target

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_sc = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        dist = abs(nx - tx) + abs(ny - ty)
        sc = -dist
        if (nx, ny) in unclaimed:
            sc += 3.5
            sc += 0.2 * ((abs(nx - cx) + abs(ny - cy)) * -1 + 14)
        if (nx, ny) in oppT:
            sc += 6.0  # flipping on entry is enabled
        if (nx, ny) in selfT:
            sc -= 0.3
        if (nx, ny) == (sx, sy):
            sc -= 0.15
        # small tie-breaker to remain deterministic
        sc += -(abs(dx) + abs(dy)) * 0.01
        if sc > best_sc:
            best_sc = sc
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]