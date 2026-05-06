def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    rpos = []
    for r in resources:
        if isinstance(r, dict):
            q = r.get("position")
            if isinstance(q, (list, tuple)) and len(q) >= 2:
                x, y = q[0], q[1]
            else:
                continue
        elif isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
        else:
            continue
        if inb(x, y) and (x, y) not in blocked:
            rpos.append((x, y))

    if not rpos:
        tx, ty = w // 2, h // 2
    else:
        best = None
        for cell in rpos:
            sd = dist((sx, sy), cell)
            od = dist((ox, oy), cell)
            # Prefer cells we can reach earlier or close to them; tie-break closer to us.
            cand = (od - sd, -sd, cell)
            if best is None or cand > best:
                best = cand
        tx, ty = best[2]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    bestm = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocked:
            continue
        # Evaluate: progress toward target + improved contest for contested resources.
        score = -dist((nx, ny), (tx, ty))
        # If any resource exists, also consider immediate contest swing deterministically.
        if rpos:
            swing_best = -10**9
            for cell in rpos:
                sd0 = dist((sx, sy), cell)
                od0 = dist((ox, oy), cell)
                sd1 = dist((nx, ny), cell)
                # opponent assumed static; maximize our advantage gain
                swing = (od0 - sd1) - (od0 - sd0)
                if swing > swing_best:
                    swing_best = swing
            score += 0.5 * swing_best
        if bestm is None or score > bestm[0] or (score == bestm[0] and dx == 0 and dy == 0):
            bestm = (score, dx, dy)

    if bestm is None:
        return [0, 0]
    return [bestm[1], bestm[2]]