def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (w - 1, h - 1)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        tx, ty = w // 2, h // 2
    else:
        # Prefer resources where we are relatively closer than opponent.
        # Advantage = (opp_dist - self_dist), tie-break by opponent closeness then coordinates.
        best_adv = None
        tx, ty = resources[0]
        for x, y in resources:
            sd = man(sx, sy, x, y)
            od = man(ox, oy, x, y)
            adv = od - sd
            key = (adv, -od, -x, -y)  # deterministic
            if best_adv is None or key > best_adv:
                best_adv = key
                tx, ty = x, y

    best_move = (0, 0)
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        if resources:
            # One-step look: estimate best advantage after move over remaining resources.
            # Keep small: only evaluate a few closest resources from new pos.
            cand = []
            for x, y in resources:
                d = man(nx, ny, x, y)
                cand.append((d, x, y))
            cand.sort()
            cand = cand[:min(5, len(cand))]
            val = -10**9
            for d, x, y in cand:
                sd = d
                od = man(ox, oy, x, y)
                adv = od - sd
                # Favor moving into nearer-to-resource positions and also away from opponent competition.
                score = 3 * adv - sd - 0.1 * od
                if score > val:
                    val = score
        else:
            val = -man(nx, ny, tx, ty)

        # Tie-break: prefer staying if equal, else lexicographic by move for determinism.
        key = (val, -dx, -dy)
        if best_val is None or key > best_val:
            best_val = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]