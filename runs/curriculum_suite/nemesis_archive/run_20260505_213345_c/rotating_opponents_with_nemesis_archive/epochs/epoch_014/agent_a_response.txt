def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if (x, y) not in obstacles:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    if not inb(sx, sy) or not resources:
        return [0, 0]

    # Choose contested/lead resource deterministically
    best = None
    for rx, ry in resources:
        ds = md(sx, sy, rx, ry)
        do = md(ox, oy, rx, ry)
        # Prefer: we are closer; then prefer larger lead; then shorter distance; then deterministic coord tie-break
        lead = do - ds
        score = (0 if ds <= do else 1, -lead, ds, rx, ry)
        if best is None or score < best[0]:
            best = (score, rx, ry)

    _, tx, ty = best

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    curd_self = md(sx, sy, tx, ty)
    curd_opp = md(ox, oy, tx, ty)

    # If opponent is much closer to the chosen target, switch to a nearby contest if possible
    if curd_opp + 1 < curd_self:
        contested = None
        for rx, ry in resources:
            ds = md(sx, sy, rx, ry)
            do = md(ox, oy, rx, ry)
            if do + 1 <= ds and do <= ds + 2:
                # Can we potentially interfere by getting closer than them next?
                score = (do, ds, rx, ry)
                if contested is None or score < contested[0]:
                    contested = (score, rx, ry)
        if contested is not None:
            _, tx, ty = contested

    bestm = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        ds2 = md(nx, ny, tx, ty)
        # Heuristic: minimize distance to our target; also slightly reduce opponent's distance to it (interference)
        do2 = md(ox, oy, tx, ty)
        # Tie-break: deterministic preference order
        step_score = (ds2, do2, nx, ny)
        if bestm is None or step_score < bestm[0]:
            bestm = (step_score, dx, dy)

    if bestm is None:
        return [0, 0]
    return [int(bestm[1]), int(bestm[2])]