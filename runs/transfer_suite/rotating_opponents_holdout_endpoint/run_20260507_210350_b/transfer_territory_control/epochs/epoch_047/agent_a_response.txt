def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    sx, sy = int(sx), int(sy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    def to_set(name):
        s = set()
        for p in observation.get(name) or []:
            if p and len(p) >= 2:
                s.add((int(p[0]), int(p[1])))
        return s

    self_terr = to_set("self_territory")
    opp_terr = to_set("opponent_territory")
    unclaimed = to_set("unclaimed_cells")

    opp_pos = observation.get("opponent_position") or [None, None]
    ox, oy = opp_pos[0], opp_pos[1]
    if ox is None or oy is None:
        ox, oy = -999, -999
    ox, oy = int(ox), int(oy)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    target_unclaimed = None
    if unclaimed:
        target_unclaimed = min(unclaimed, key=lambda p: abs(p[0]-sx) + abs(p[1]-sy))

    target_opp = None
    if opp_terr:
        target_opp = min(opp_terr, key=lambda p: abs(p[0]-sx) + abs(p[1]-sy))

    best_move = [0, 0]
    best_val = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        val = 0.0
        if (nx, ny) in self_terr:
            val += 0.2
        elif (nx, ny) in unclaimed:
            val += 1.2
        elif (nx, ny) in opp_terr:
            val += 2.1
        else:
            val += 0.0

        if target_unclaimed is not None:
            dist_now = abs(sx - target_unclaimed[0]) + abs(sy - target_unclaimed[1])
            dist_next = abs(nx - target_unclaimed[0]) + abs(ny - target_unclaimed[1])
            val += 0.25 * (dist_now - dist_next)

        if target_opp is not None:
            dist_now = abs(sx - target_opp[0]) + abs(sy - target_opp[1])
            dist_next = abs(nx - target_opp[0]) + abs(ny - target_opp[1])
            val += 0.35 * (dist_now - dist_next)

        if ox != -999:
            dopp_now = abs(sx - ox) + abs(sy - oy)
            dopp_next = abs(nx - ox) + abs(ny - oy)
            val += 0.08 * (dopp_now - dopp_next)

        if (nx, ny) in self_terr or (nx, ny) in unclaimed or (nx, ny) in opp_terr:
            val += 0.01 * (nx + ny)

        if val > best_val + 1e-12:
            best_val = val
            best_move = [dx, dy]
        elif abs(val - best_val) <= 1e-12:
            if [dx, dy] < best_move:
                best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]