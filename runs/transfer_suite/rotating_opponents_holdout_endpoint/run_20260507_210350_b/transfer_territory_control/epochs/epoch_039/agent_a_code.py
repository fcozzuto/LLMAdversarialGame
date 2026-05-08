def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        obstacles.add((int(p[0]), int(p[1])))

    resources = set()
    for p in observation.get("resources", []) or []:
        resources.add((int(p[0]), int(p[1])))

    unclaimed = set()
    for c in observation.get("unclaimed_cells", []) or []:
        unclaimed.add((int(c[0]), int(c[1])))

    self_terr = set()
    for c in observation.get("self_territory", []) or []:
        self_terr.add((int(c[0]), int(c[1])))

    rem_res = int(observation.get("remaining_resource_count", 0) or 0)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    best_dx, best_dy, best_sc = 0, 0, -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        sc = 0
        d_to_opp = man(nx, ny, ox, oy)
        sc += 2 * (d_to_opp - man(sx, sy, ox, oy))

        if rem_res > 0 and resources:
            d = min(man(nx, ny, rx, ry) for (rx, ry) in resources)
            sc += 50 - 10 * d
        else:
            if (nx, ny) in unclaimed:
                sc += 80
            elif (nx, ny) in self_terr:
                sc += 15
            else:
                sc -= 5

            if unclaimed:
                d_un = min(man(nx, ny, ux, uy) for (ux, uy) in unclaimed)
                sc += 40 - 8 * d_un

        if (nx, ny) in unclaimed and (nx, ny) in self_terr:
            sc += 50

        if sc > best_sc or (sc == best_sc and (dx, dy) == (0, 0)):
            best_sc = sc
            best_dx, best_dy = dx, dy

    return [int(best_dx), int(best_dy)]