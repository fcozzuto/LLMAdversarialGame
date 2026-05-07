def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocked = set()
    for p in observation.get("obstacles", []) or []:
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))
        except:
            pass

    resources = []
    for r in observation.get("resources", []) or []:
        try:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                resources.append((x, y))
        except:
            pass

    if not resources:
        return [0, 0]

    def cheb(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    resources_sorted = sorted(resources, key=lambda p: (p[1], p[0]))  # deterministic tie-break

    best_move = (0, 0)
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        my = (nx, ny)
        # Prefer: reach a resource before opponent; avoid being lured onto opponent-dominant positions.
        val = 0
        chosen = resources_sorted[0]
        for r in resources_sorted:
            myd = cheb(my, r)
            opd = cheb((ox, oy), r)
            # large win when my distance is strictly smaller
            if myd < opd:
                pref = (opd - myd) * 3 + (5 - myd)
            elif myd == opd:
                pref = -2  # tie: be careful
            else:
                pref = -(myd - opd) * 4
            # minor bias toward upward progress (y) to stabilize
            prog = -(r[1] - ny) if r[1] > ny else 0
            # small penalty if resource is on same row as opponent (often contested in deniers)
            contest = 6 if r[1] == oy else 0
            score = pref + prog - contest
            # maximize score
            if score > val:
                val = score
                chosen = r

        # Second-stage tie-break: closer to chosen target; then deterministically smaller move
        final = (-val, cheb(my, chosen), dx, dy)
        if best_val is None or final < best_val:
            best_val = final
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]