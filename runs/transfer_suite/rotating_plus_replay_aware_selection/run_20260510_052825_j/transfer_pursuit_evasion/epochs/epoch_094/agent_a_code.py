def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    role = str(observation.get("self_role") or "").lower()
    evader = ("evader" in role) or ("escape" in role) or ("runner" in role) or ("hider" in role)

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def dist2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    def free_neighbors(x, y):
        c = 0
        for dx, dy in deltas:
            nx, ny = x + dx, y + dy
            if free(nx, ny):
                c += 1
        return c

    best = None
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue

        if capture := (nx == ox and ny == oy):
            return [dx, dy]

        d = dist2(nx, ny, ox, oy)

        fn = free_neighbors(nx, ny)
        # local trap: prefer higher mobility for evader; prefer lower mobility for pursuer (to corner opponent indirectly)
        trap = 8 - fn  # larger => more trapped

        # wall pressure: discourage staying still if movement helps distance (deterministic tie-break)
        still = 1 if (dx == 0 and dy == 0) else 0

        # obstacle proximity: compute nearest obstacle manhattan (min over at most a few nearby-ish cells via scan)
        min_obst = 99
        for ox2, oy2 in blocked:
            dd = abs(nx - ox2) + abs(ny - oy2)
            if dd < min_obst:
                min_obst = dd
                if min_obst == 0:
                    break

        # score
        if evader:
            val = d * 10.0 + fn * 1.5 - trap * 0.2 + min_obst * 0.25 - still * 0.4
        else:
            val = (-d) * 10.0 + (8 - trap) * 0.2 + min_obst * 0.08 - still * 0.1

        if best_val is None or val > best_val:
            best_val = val
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]