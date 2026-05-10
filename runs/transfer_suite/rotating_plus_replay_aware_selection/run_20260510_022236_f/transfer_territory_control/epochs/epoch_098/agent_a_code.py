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

    self_terr = set(map(tuple, observation.get("self_territory") or []))
    op_terr = set(map(tuple, observation.get("opponent_territory") or []))
    unclaimed = list(map(tuple, observation.get("unclaimed_cells") or []))
    if not unclaimed:
        unclaimed = list(op_terr)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, 0), (0, -1), (0, 0), (0, 1), (1, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]

    best = None
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        if unclaimed:
            cx, cy = unclaimed[0]
            bd = (cx - nx) * (cx - nx) + (cy - ny) * (cy - ny)
            for i in range(1, min(30, len(unclaimed))):
                tx, ty = unclaimed[i]
                d = (tx - nx) * (tx - nx) + (ty - ny) * (ty - ny)
                if d < bd:
                    bd = d
        else:
            bd = (ox - nx) * (ox - nx) + (oy - ny) * (oy - ny)

        to_claim = -bd
        avoid_op = -5000 if (nx, ny) in op_terr else 0
        stay_in_self = 80 if (nx, ny) in self_terr else 0
        dist_to_opp = -((ox - nx) * (ox - nx) + (oy - ny) * (oy - ny)) // 50

        score = to_claim + avoid_op + stay_in_self + dist_to_opp
        if best is None or score > best_score or (score == best_score and (dx, dy) == (0, 0)):
            best, best_score = [dx, dy], score

    if best is None:
        return [0, 0]
    return best