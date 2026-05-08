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

    unclaimed = set()
    for p in observation.get("unclaimed_cells") or []:
        if p and len(p) >= 2:
            unclaimed.add((int(p[0]), int(p[1])))

    resources = observation.get("resources") or []
    res0 = None
    for p in resources:
        if p and len(p) >= 2:
            res0 = (int(p[0]), int(p[1]))
            break

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h
    def md(a, b, c, d):
        dx = a - c
        dy = b - d
        return abs(dx) + abs(dy)

    best = (float("-inf"), 0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        score = 0
        if (nx, ny) in opp_tr:
            score += 6
        elif (nx, ny) in unclaimed:
            score += 4
        elif (nx, ny) in self_tr:
            score += 1

        # Prefer approaching opponent and, when available, the first resource.
        score += -0.15 * md(nx, ny, ox, oy)
        if res0 is not None:
            score += -0.10 * md(nx, ny, res0[0], res0[1])

        # Mild tie-break: keep moving away from obstacles by favoring non-edgeless transitions.
        if (nx, ny) in self_tr:
            score += -0.01 * md(nx, ny, sx, sy)

        if score > best[0] or (score == best[0] and (dx, dy) < (best[1], best[2])):
            best = (score, dx, dy)

    if best[0] == float("-inf"):
        return [0, 0]
    return [int(best[1]), int(best[2])]