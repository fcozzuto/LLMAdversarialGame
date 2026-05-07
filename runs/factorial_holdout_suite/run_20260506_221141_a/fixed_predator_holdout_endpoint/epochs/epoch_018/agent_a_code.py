def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    turns_remaining = int(observation.get("turns_remaining", 0))

    obst = set()
    for p in obstacles:
        try:
            obst.add((int(p[0]), int(p[1])))
        except Exception:
            pass

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    # Candidate move preference order (deterministic tie-break)
    moves = [(-1, 0), (0, -1), (0, 0), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]

    if not resources:
        # Drift to center while avoiding obstacles, slight bias away from opponent.
        cx, cy = w // 2, h // 2
        best = -10**18
        bestm = (0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not in_bounds(nx, ny) or (nx, ny) in obst:
                continue
            sd = man(nx, ny, cx, cy)
            od = man(nx, ny, ox, oy)
            v = (-sd * 1.0) + (od * 0.02) - (abs(nx - sx) + abs(ny - sy)) * 0.001
            if v > best:
                best, bestm = v, (dx, dy)
        return [int(bestm[0]), int(bestm[1])]

    def cell_value(px, py):
        best = -10**18
        for rx, ry in resources:
            sd = man(px, py, rx, ry)
            od = man(ox, oy, rx, ry)
            # Core: prefer resources where we are closer than opponent.
            adv = od - sd  # positive => we're closer
            closeness_bonus = -0.12 * sd + 0.03 * od
            denier_bias = 2.4 * adv
            urgent = 1.0 + (0.6 if turns_remaining <= 8 else 0.0) - 0.05 * sd
            # If very close to some resource, strongly commit.
            commit = 2.0 if sd == 0 else (1.0 if sd == 1 else 0.0)
            v = denier_bias + closeness_bonus + urgent * 0.01 + commit
            if v > best:
                best = v
        return best

    bestv = -10**18
    bestm = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obst:
            continue
        v = cell_value(nx, ny)
        # Gentle penalty for moves that don't improve Manhattan to best resource set
        if v > bestv:
            bestv, bestm = v, (dx, dy)

    return [int(bestm[0]), int(bestm[1])]