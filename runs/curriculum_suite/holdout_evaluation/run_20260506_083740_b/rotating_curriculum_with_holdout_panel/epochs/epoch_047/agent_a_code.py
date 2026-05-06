def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    ob = set()
    for p in obstacles:
        if p and len(p) >= 2:
            ob.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inb(x, y) and (x, y) not in ob

    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not resources:
        best = (0, 0)
        bestv = -10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            v = md(nx, ny, ox, oy) - md(sx, sy, ox, oy)
            if v > bestv or (v == bestv and (dx, dy) < best):
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    scored_targets = []
    for r in resources:
        if not r or len(r) < 2:
            continue
        rx, ry = int(r[0]), int(r[1])
        if not valid(rx, ry):
            continue
        dme = md(sx, sy, rx, ry)
        dop = md(ox, oy, rx, ry)
        # Favor resources where we are relatively ahead; otherwise, delay chasing opponent by taking "still winnable" cells.
        rel = dop - dme  # bigger means we are closer
        risk = -dme  # prefer not-too-far if rel ties
        scored_targets.append((rel, risk, dme, rx, ry))
    scored_targets.sort(reverse=True)
    # choose from top few deterministically to avoid getting stuck on a single niche
    target_list = scored_targets[:3] if scored_targets else []
    if not target_list:
        return [0, 0]

    def move_value(dx, dy):
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            return -10**12
        best_comp = -10**12
        for rel, _, dme, rx, ry in target_list:
            ndme = md(nx, ny, rx, ry)
            ndop = md(ox, oy, rx, ry)
            comp = (ndop - ndme)
            # Encourage progress toward chosen target and discourages "widening" our lead loss
            progress = (dme - ndme)
            comp2 = comp * 2 + progress
            if comp2 > best_comp:
                best_comp = comp2
        # Mild safety: avoid moving closer to obstacles' neighborhood is complex; instead cap bad moves by self-out-of-bounds already handled.
        return best_comp

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        v = move_value(dx, dy)
        if v > best_val or (v == best_val and (dx, dy) < best_move):
            best_val = v
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]