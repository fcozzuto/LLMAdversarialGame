def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = int(observation.get("grid_width", 1)) or 1
    h = int(observation.get("grid_height", 1)) or 1

    def to_xy(v):
        if isinstance(v, (list, tuple)) and len(v) >= 2:
            return int(v[0]), int(v[1])
        return None

    obst = set()
    for p in observation.get("obstacles", []) or []:
        t = to_xy(p)
        if t is not None:
            obst.add(t)

    resources = []
    for r in observation.get("resources", []) or []:
        t = to_xy(r)
        if t is not None:
            resources.append(t)

    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(ax, ay, bx, by):
        d = ax - bx
        if d < 0:
            d = -d
        e = ay - by
        if e < 0:
            e = -e
        return d + e

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    best_movescore = -10**18
    best_move = (0, 0)

    # Pick the single resource where we have the greatest "lead" (opp closer => negative).
    best_target = resources[0]
    best_lead = man(ox, oy, resources[0][0], resources[0][1]) - man(sx, sy, resources[0][0], resources[0][1])
    for rx, ry in resources[1:]:
        lead = man(ox, oy, rx, ry) - man(sx, sy, rx, ry)
        if lead > best_lead:
            best_lead = lead
            best_target = (rx, ry)

    tx, ty = best_target

    # Move to improve our advantage to the chosen target; deterministic tie-break: smallest dx, then dy.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obst:
            continue
        cur_score = man(ox, oy, tx, ty) - man(nx, ny, tx, ty)
        if cur_score > best_movescore:
            best_movescore = cur_score
            best_move = (dx, dy)
        elif cur_score == best_movescore:
            if (dx, dy) < best_move:
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]