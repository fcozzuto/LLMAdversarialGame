def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", (0, 0))
    op = observation.get("opponent_position", (w - 1, h - 1))
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

    def dist(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    opp_pos = (ox, oy)

    if resources:
        # Global target preference: resources we can beat the opponent to.
        best_global = None
        best_gscore = -10**9
        for tx, ty in resources:
            our_d = dist((sx, sy), (tx, ty))
            opp_d = dist(opp_pos, (tx, ty))
            gscore = (opp_d - our_d) * 10 - our_d + (-(tx + ty) * 0.001)
            if gscore > best_gscore:
                best_gscore = gscore
                best_global = (tx, ty)
    else:
        best_global = (w // 2, h // 2)

    def eval_from(pos):
        # Evaluate best immediate future target from a candidate position.
        if resources:
            best = -10**9
            for tx, ty in resources:
                our_d = dist(pos, (tx, ty))
                opp_d = dist(opp_pos, (tx, ty))
                # Strongly prioritize winning races to resources.
                s = (opp_d - our_d) * 12 - our_d
                # Small deterministic bias to prefer higher (x,y).
                s += (tx * 0.01 + ty * 0.001)
                if s > best:
                    best = s
            return best
        # No resources: head toward the center.
        cx, cy = w // 2, h // 2
        return -dist(pos, (cx, cy))

    best_move = [0, 0]
    best_val = -10**18
    # Prefer staying still only if clearly best; otherwise move toward the preferred target/race.
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        pos = (nx, ny)
        v = eval_from(pos)
        if best_global is not None:
            v += -dist(pos, best_global) * 0.5
        if v > best_val:
            best_val = v
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]