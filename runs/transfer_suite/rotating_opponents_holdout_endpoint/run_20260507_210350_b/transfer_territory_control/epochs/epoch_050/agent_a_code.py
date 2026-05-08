def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    self_tr = set()
    for p in observation.get("self_territory") or []:
        if p and len(p) >= 2:
            self_tr.add((int(p[0]), int(p[1])))

    opp_tr = set()
    for p in observation.get("opponent_territory") or []:
        if p and len(p) >= 2:
            opp_tr.add((int(p[0]), int(p[1])))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            resources.append((int(p[0]), int(p[1])))

    unclaimed = []
    for p in observation.get("unclaimed_cells") or []:
        if p and len(p) >= 2:
            unclaimed.append((int(p[0]), int(p[1])))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def best_target():
        if resources:
            return resources[0]
        if unclaimed:
            # prefer unclaimed near our boundary and closer to center; tie-break deterministically
            best = None
            best_score = -10**9
            for ux, uy in unclaimed:
                if not inb(ux, uy):
                    continue
                adj_self = 0
                adj_opp = 0
                for dx, dy in dirs:
                    xx, yy = ux - dx, uy - dy
                    if (xx, yy) in self_tr:
                        adj_self = 1
                    if (xx, yy) in opp_tr:
                        adj_opp = 1
                s = 6 * adj_self + 3 * adj_opp - (abs(ux - sx) + abs(uy - sy)) * 0.35 - ((ux - cx) ** 2 + (uy - cy) ** 2) * 0.01
                if s > best_score or (s == best_score and (uy, ux) < (best[1], best[0])):
                    best_score = s
                    best = (ux, uy)
            return best
        return (ox, oy)

    tx, ty = best_target()
    candidate_moves = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            val = -10**9
        else:
            if (nx, ny) in self_tr:
                base = 1
            elif (nx, ny) in opp_tr:
                base = 4  # flipping on entry
            else:
                base = 2 if (nx, ny) in set(unclaimed) else 0  # unclaimed priority
            # also drive toward target, but softly repel from opponent (to avoid getting trapped)
            dist_to_t = abs(nx - tx) + abs(ny - ty)
            dist_to_o = abs(nx - ox) + abs(ny - oy)
            val = base + (6 - dist_to_t) * 0.6 + dist_to_o * 0.02
            if dx == 0 and dy == 0:
                val -= 0.15
        candidate_moves.append((val, dy, dx))
    candidate_moves.sort(reverse=True)
    _, dy, dx = candidate_moves[0]
    return [int(dx), int(dy)]