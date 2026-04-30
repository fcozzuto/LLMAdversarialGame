def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    res_set = set(resources)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def d2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    def clamp01(v):
        return 1.0 if v > 0 else 0.0

    best = (0, 0)
    bestv = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue

        # Move safety vs opponent: prefer not to get too close unless collecting.
        opp_dist = d2(nx, ny, ox, oy)
        safety = -0.12 * opp_dist

        # If collecting immediately, add a strong bonus.
        collect = 1.0 if (nx, ny) in res_set else 0.0

        # Target evaluation: choose the best resource for "likely ownership".
        if resources:
            best_res = -10**18
            for rx, ry in resources:
                myd = d2(nx, ny, rx, ry)
                opd = d2(ox, oy, rx, ry)

                # Prefer resources we are not farther from; closer gets higher.
                win_margin = (opd - myd)  # positive => we are closer
                ownership = 1.0 if myd <= opd else 0.0

                # Encourage closeness; also encourage stealing (win_margin positive).
                score = (ownership * 6000.0) + (win_margin * 1.2) + (0.0 if myd == 0 else 12000.0 / myd)
                # Slightly prefer resources aligned with moving toward opponent corner (diagonal progress).
                prog = (nx + (h - 1 - ny))  # deterministic direction bias
                score += 0.5 * prog
                if score > best_res:
                    best_res = score
        else:
            # No visible resources: go toward opponent with small safety.
            best_res = -d2(nx, ny, ox, oy) * 0.9

        val = safety + (collect * 20000.0) + best_res

        # Add small deterministic tie-break: favor moves that reduce distance to opponent.
        val += -0.001 * d2(nx, ny, ox, oy)

        if val > bestv:
            bestv = val
            best = (dx, dy)

    return [int(best[0]), int(best[1])]