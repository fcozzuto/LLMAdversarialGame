def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    if not resources:
        return [0, 0]

    best = None  # (slack, -ds, rx, ry)
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        ds = dist(sx, sy, rx, ry)
        do = dist(ox, oy, rx, ry)
        slack = do - ds
        key = (slack, -ds)
        if best is None or key > best[0:2]:
            best = (slack, -ds, rx, ry)

    if best is None:
        return [0, 0]

    _, _, tx, ty = best
    if sx == tx and sy == ty:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    bestm = None
    bestscore = None

    cur_ds = dist(sx, sy, tx, ty)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        nds = dist(nx, ny, tx, ty)
        ndo = dist(ox, oy, tx, ty)
        slack = ndo - nds
        # Prefer moves that improve capture likelihood; slightly discourage moving toward opponent.
        opp_closeness = -dist(nx, ny, ox, oy)
        score = (slack * 10) + (-(nds)) + (opp_closeness * 0.1)
        if bestscore is None or score > bestscore or (score == bestscore and (nds < cur_ds)):
            bestscore = score
            bestm = (dx, dy)

    if bestm is None:
        return [0, 0]
    return [int(bestm[0]), int(bestm[1])]