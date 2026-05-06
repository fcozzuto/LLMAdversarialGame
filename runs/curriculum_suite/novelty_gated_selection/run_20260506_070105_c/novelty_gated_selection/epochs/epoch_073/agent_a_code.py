def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for o in observation.get("obstacles", []) or []:
        if o is not None and len(o) >= 2:
            obstacles.add((int(o[0]), int(o[1])))

    resources = []
    for r in observation.get("resources", []) or []:
        if r is not None and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if (rx, ry) not in obstacles:
                resources.append((rx, ry))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def dist(ax, ay, bx, by): return abs(ax - bx) + abs(ay - by)

    # Deterministic move preference order (dx,dy)
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_sc = -10**18

    # If no resources, drift to increase distance from opponent while heading to center-ish
    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            sc = dist(nx, ny, ox, oy) - 0.15 * dist(nx, ny, tx, ty)
            if sc > best_sc:
                best_sc = sc
                best = [dx, dy]
        return best if best is not None else [0, 0]

    # Otherwise: choose move that maximizes immediate advantage on contestable resources
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        self_opp = dist(nx, ny, ox, oy)
        # best advantage if we aim for the most favorable resource from this next cell
        adv = -10**18
        for rx, ry in resources:
            sd = dist(nx, ny, rx, ry)
            od = dist(ox, oy, rx, ry)
            # prioritize resources where we're closer; also slightly prefer lower self distance to reduce wandering
            val = (od - sd) - 0.03 * sd
            if val > adv:
                adv = val
        sc = adv - 0.02 * self_opp
        if sc > best_sc:
            best_sc = sc
            best = [dx, dy]

    return best if best is not None else [0, 0]