def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    best = (-10**9, 0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        gain = 0
        if (nx, ny) in unclaimed:
            gain += 50
        # Prefer moves adjacent to unclaimed cells
        cnt = 0
        for ex in (-1, 0, 1):
            for ey in (-1, 0, 1):
                if ex == 0 and ey == 0:
                    continue
                ax, ay = nx + ex, ny + ey
                if inb(ax, ay) and (ax, ay) in unclaimed:
                    cnt += 1
        gain += 7 * cnt
        # Avoid stepping onto opponent; small penalty for proximity
        if (nx, ny) == (ox, oy):
            gain -= 100000
        else:
            dist = abs(nx - ox) + abs(ny - oy)
            gain -= min(20, dist)
        if (gain, -dx, -dy) > best:
            best = (gain, dx, dy)

    if best[0] < -10**8:
        return [0, 0]
    return [best[1], best[2]]