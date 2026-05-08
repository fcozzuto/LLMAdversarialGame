def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in (observation.get("resources") or []):
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def manhattan(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx + dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = (0, 0)
    bestv = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        if resources:
            bestd = 10**9
            besttie = 10**9
            for rx, ry in resources:
                if (rx, ry) == (nx, ny):
                    bestd = 0
                    besttie = 0
                    break
                d = manhattan(nx, ny, rx, ry)
                if d < bestd or (d == bestd and (rx + ry) < besttie):
                    bestd = d
                    besttie = rx + ry

            do = manhattan(nx, ny, ox, oy)
            # Prefer faster capture, avoid denier by staying away from opponent.
            v = -bestd * 100 - do * 3 + (0 if (nx, ny) in resources else 0)
            # Small bias to move towards resources along diagonal-ish to speed up.
            v += -abs((nx - sx) - (ny - sy)) * 0.5
        else:
            # No visible resources: drift toward opponent of remaining pool by heading to nearest corner-resources line.
            # Deterministic: aim toward opposite corner relative to opponent start.
            target_x = 0 if ox > (w - 1) // 2 else w - 1
            target_y = 0 if oy > (h - 1) // 2 else h - 1
            d = manhattan(nx, ny, target_x, target_y)
            v = -d + (manhattan(nx, ny, ox, oy) * 0.2)

        if v > bestv:
            bestv = v
            best = (dx, dy)

    return [int(best[0]), int(best[1])]