def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for o in observation.get("obstacles", []) or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            obstacles.add((int(o[0]), int(o[1])))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            resources.append((int(r[0]), int(r[1])))
    res_set = set(resources)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1), (0, 0)]

    # If any resource reachable this turn, take it deterministically.
    best = (-10**18, 0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        if (nx, ny) in res_set:
            d = 0
            opp_d = dist((nx, ny), (ox, oy))
            sc = 10**12 + 10 * opp_d - (nx + ny)  # deterministic tie-break
        else:
            if resources:
                target = min(resources, key=lambda p: dist((sx, sy), p))
                d = dist((nx, ny), target)
            else:
                d = dist((nx, ny), (ox, oy))
            opp_d = dist((nx, ny), (ox, oy))

            # Resource race / denial: don't step near opponent unless it helps you capture soon.
            capture_pressure = 0
            if resources:
                # how soon we can reach any resource from (nx, ny)
                capture_pressure = -min(dist((nx, ny), r) for r in resources)

            sc = -d + 0.6 * opp_d + 1.2 * capture_pressure
            # Discourage moves that land on squares in opponent's immediate neighborhood (pool-like deniers).
            if dist((nx, ny), (ox, oy)) <= 1:
                sc -= 2.5

            # Light preference to progress toward the closest resource direction.
            if resources:
                tx, ty = min(resources, key=lambda p: dist((sx, sy), p))
                sc += 0.1 * (abs(tx - sx) + abs(ty - sy) - (abs(tx - nx) + abs(ty - ny)))

        if sc > best[0] or (sc == best[0] and (dx, dy) < (best[1], best[2])):
            best = (sc, dx, dy)

    return [int(best[1]), int(best[2])]