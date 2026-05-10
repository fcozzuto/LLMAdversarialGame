def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    sx, sy = int(sx), int(sy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    selfT = set()
    for p in observation.get("self_territory") or []:
        if p and len(p) >= 2:
            selfT.add((int(p[0]), int(p[1])))

    opT = set()
    for p in observation.get("opponent_territory") or []:
        if p and len(p) >= 2:
            opT.add((int(p[0]), int(p[1])))

    unT = set()
    for p in observation.get("unclaimed_cells") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                unT.add((x, y))

    cx, cy = w // 2, h // 2

    def centroid(cells):
        if not cells:
            return (cx, cy)
        sx2 = 0
        sy2 = 0
        n = 0
        for x, y in cells:
            sx2 += x
            sy2 += y
            n += 1
        return (sx2 // n, sy2 // n)

    target = centroid(opT if opT else unT)
    tx, ty = target

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = [0, 0]
    bestv = -10**9

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            nx, ny = sx, sy
            dx, dy = 0, 0

        cell_type = 0
        if (nx, ny) in opT:
            cell_type = 5
        elif (nx, ny) in unT:
            cell_type = 3
        elif (nx, ny) in selfT:
            cell_type = 1
        else:
            cell_type = 0

        # Favor reducing distance to opponent centroid; also prefer moving off our current cell.
        dist_to_op = abs(nx - tx) + abs(ny - ty)
        dist_to_our_center = abs(nx - cx) + abs(ny - cy)

        # Deterministic tiebreaker: fewer step cost, then lexicographic move.
        step_cost = abs(dx) + abs(dy)
        v = cell_type * 1000 - dist_to_op * 7 - dist_to_our_center - step_cost * 2
        if observation.get("turn_index", 0) % 10 == 9:
            # Near the leader-bonus turn: try to drift toward board center line.
            v += -dist_to_our_center * 3

        if v > bestv:
            bestv = v
            best = [dx, dy]

    return best