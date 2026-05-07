def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(0, 0), (-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1)]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources:
        # Fallback: push toward center-ish while denying proximity to opponent.
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            v = -man(nx, ny, int(cx), int(cy)) - 0.5 * man(nx, ny, ox, oy)
            if best is None or v > best:
                best = v
                bd = (dx, dy)
        return [bd[0], bd[1]]

    # Prefer resources we can reach before the opponent (distance advantage),
    # else pick the closest resource to race to.
    scored_targets = []
    for rx, ry in resources:
        ds = man(sx, sy, rx, ry)
        do = man(ox, oy, rx, ry)
        adv = ds - do  # negative => we are closer
        # If equal, prefer higher absolute distance (to avoid easy steals) + resource bias by ds
        weight = (-1 if adv < 0 else 1) * abs(adv) - 0.1 * ds + (0.01 if adv == 0 else 0.0)
        scored_targets.append((weight, ds, do, rx, ry))
    scored_targets.sort(reverse=True)
    # Take top few deterministically to reduce brittle single-choice behavior.
    top = scored_targets[:3] if len(scored_targets) >= 3 else scored_targets

    best_move = (0, 0)
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        # Evaluate next step against multiple candidate targets.
        worst_case = None
        for _, ds, do, rx, ry in top:
            nds = man(nx, ny, rx, ry)
            ndo = man(ox, oy, rx, ry)  # opponent position unchanged this turn
            # If we are closer, score strongly; if not, penalize.
            turn_adv = nds - ndo
            s = (-1000 if turn_adv < 0 else 0) + (-turn_adv * 10) + (-nds) + (0.2 * do)
            if worst_case is None or s < worst_case:
                worst_case = s
        # Also discourage stepping adjacent to obstacles too often via local penalty.
        adj_obst = 0
        for ax, ay in ((1,0),(-1,0),(0,1),(0,-1)):
            tx, ty = nx + ax, ny + ay
            if (tx, ty) in obstacles:
                adj_obst += 1
        total = worst_case - 0.3 * adj_obst
        if best_score is None or total > best_score:
            best_score = total
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]