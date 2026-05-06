def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    obst = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obst.add((int(p[0]), int(p[1])))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            resources.append((int(r[0]), int(r[1])))

    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = (0, 0)
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = int(sx) + dx, int(sy) + dy
        if not inb(nx, ny) or (nx, ny) in obst:
            continue

        my_best = -10**18
        for rx, ry in resources:
            md = man(nx, ny, rx, ry)
            od = man(int(ox), int(oy), rx, ry)
            adv = od - md  # positive => we are closer to this resource than opponent
            my_best = max(my_best, adv * 1000 - md)  # prefer bigger advantage, then shorter distance

        # If no valid target, fall back to simply staying safe-ish (min distance to nearest resource)
        if my_best == -10**18:
            md_min = min(man(nx, ny, rx, ry) for rx, ry in resources)
            my_best = -md_min

        # Deterministic tie-break
        score = my_best - (dx * 0.001 + dy * 0.0001)
        if score > best_score:
            best_score = score
            best = (dx, dy)

    return [int(best[0]), int(best[1])]