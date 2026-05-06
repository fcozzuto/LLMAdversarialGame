def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def legal(x, y):
        return inb(x, y) and (x, y) not in blocked

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    targets = []
    for r in resources:
        if isinstance(r, dict):
            pos = r.get("position", None)
            if isinstance(pos, (list, tuple)) and len(pos) >= 2:
                targets.append((pos[0], pos[1]))
        elif isinstance(r, (list, tuple)) and len(r) >= 2:
            targets.append((r[0], r[1]))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cx, cy = (w - 1) // 2, (h - 1) // 2

    best = None
    bestv = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        if targets:
            best_adv = -10**18
            best_my = 10**9
            for tx, ty in targets:
                dself = man(nx, ny, tx, ty)
                dopp = man(ox, oy, tx, ty)
                adv = dopp - dself
                # strong bias to grab/beat opponent, still allow contesting
                if adv >= 0:
                    adv = adv * 4 + (dself == 0) * 100
                else:
                    adv = adv * 2 - dself
                if adv > best_adv:
                    best_adv = adv
                if dself < best_my:
                    best_my = dself
            # small tie-break: keep distance from opponent unless it helps to secure
            opp_dist = man(nx, ny, ox, oy)
            v = best_adv + max(0, 10 - best_my) + (opp_dist // 2)
        else:
            v = -man(nx, ny, cx, cy) + (man(nx, ny, ox, oy) // 2)

        if v > bestv:
            bestv = v
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best