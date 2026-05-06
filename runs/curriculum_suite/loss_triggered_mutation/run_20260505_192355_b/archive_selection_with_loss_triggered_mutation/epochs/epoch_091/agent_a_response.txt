def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles", []) or []
    obst = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = observation.get("resources", []) or []
    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                res.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    def kingdist(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    def legal_after(dx, dy):
        nx, ny = sx + dx, sy + dy
        return (dx, dy) if inb(nx, ny) else None

    # If no resources, just creep toward center to reduce being boxed.
    if not res:
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        best = None
        for dx, dy in moves:
            la = legal_after(dx, dy)
            if la:
                nx, ny = sx + dx, sy + dy
                d = (cx - nx) ** 2 + (cy - ny) ** 2
                if best is None or d < best[0] or (d == best[0] and (dx, dy) < best[1]):
                    best = (d, (dx, dy))
        return list(best[1]) if best else [0, 0]

    # Evaluate each candidate move by best "lead" over opponent for any reachable resource.
    best_move = None
    best_score = None
    for dx, dy in moves:
        la = legal_after(dx, dy)
        if not la:
            continue
        nx, ny = sx + dx, sy + dy
        self_pos = (nx, ny)
        # Lead heuristic: larger is better; add small tie-breaks for progress to a chosen resource.
        lead_best = None
        for tx, ty in res:
            target = (tx, ty)
            sd = kingdist(self_pos, target)
            od = kingdist((ox, oy), target)
            # Strongly prefer immediate reach, then larger lead, then shorter self distance.
            lead = od - sd
            cand = (lead, -sd)
            if lead_best is None or cand > lead_best:
                lead_best = cand
        # If all resources are losing, still move that minimizes opponent advantage.
        # Add deterministic tie-break: prefer moving closer to center (slight).
        center_dx = nx - (w - 1) / 2.0
        center_dy = ny - (h - 1) / 2.0
        center_pen = center_dx * center_dx + center_dy * center_dy
        score = (lead_best[0], lead_best[1], -center_pen)
        if best_score is None or score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])] if best_move else [0, 0]