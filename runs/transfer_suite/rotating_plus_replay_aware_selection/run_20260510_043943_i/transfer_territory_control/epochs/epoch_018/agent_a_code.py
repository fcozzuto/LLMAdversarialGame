def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    obst = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obst.add((int(p[0]), int(p[1])))

    self_set = set()
    for p in observation.get("self_territory", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            self_set.add((int(p[0]), int(p[1])))

    opp_set = set()
    for p in observation.get("opponent_territory", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            opp_set.add((int(p[0]), int(p[1])))

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            resources.append((int(p[0]), int(p[1])))

    unclaimed = []
    for p in observation.get("unclaimed_cells", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            unclaimed.append((int(p[0]), int(p[1])))

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    targets = resources if resources else (unclaimed if unclaimed else [])
    if not targets:
        targets = [(int(cx), int(cy))]

    # Pick a deterministic target biased toward nearby expansion points.
    best_t = None
    best_td = None
    for tx, ty in targets:
        d = man(sx, sy, tx, ty)
        # Small bias toward cells that are likely to be claimed by moving forward.
        bias = 0
        if (tx, ty) in opp_set:
            bias -= 0.8
        if (tx, ty) in self_set:
            bias += 0.2
        td = d + bias
        if best_t is None or td < best_td or (td == best_td and (ty, tx) < (best_t[1], best_t[0])):
            best_t, best_td = (tx, ty), td
    tx, ty = best_t

    best_move = [0, 0]
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obst:
            continue

        d_t = man(nx, ny, tx, ty)
        d_op = man(nx, ny, ox, oy)

        # Encourage expansion (entering new cells) and occasional flipping (entering opponent cells).
        new_bonus = 0.0 if (nx, ny) in self_set else 0.9
        flip_bonus = 0.0 if (nx, ny) not in opp_set else 1.1

        # Keep distance from opponent a bit to limit their center claim pressure.
        score = (-d_t) + (0.22 * d_op) + new_bonus + flip_bonus

        if best_score is None or score > best_score or (score == best_score and (dx, dy) < (best_move[0], best_move[1])):
            best_score = score
            best_move = [dx, dy]

    return best_move