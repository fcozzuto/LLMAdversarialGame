def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    tr = int(observation.get("turns_remaining", 0))

    obs = set()
    for x, y in obstacles:
        obs.add((int(x), int(y)))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    valid = []
    for x, y in resources:
        x, y = int(x), int(y)
        if inb(x, y) and (x, y) not in obs:
            valid.append((x, y))

    if not valid:
        return [0, 0]

    best = None
    for rx, ry in valid:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        lead = do - ds
        # If late in game, reduce opponent-lead obsession and just minimize our distance.
        score = (lead * 10) + (-ds) + (2 if ds == 0 else 0) + (1 if (tr > 0 and ds <= tr) else 0)
        if best is None or score > best[0] or (score == best[0] and ds < best[1]):
            best = (score, ds, rx, ry)
    tx, ty = best[2], best[3]

    deltas = [(-1,-1), (0,-1), (1,-1), (-1,0), (0,0), (1,0), (-1,1), (0,1), (1,1)]
    best_move = (None, None)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        nds = cheb(nx, ny, tx, ty)
        ndo = cheb(ox, oy, tx, ty)
        # Try to get closer; if opponent also close, choose moves that keep our lead.
        lead_after = ndo - nds
        # Tiny deterministic tie-break: prefer moving in positive x then positive y.
        tie = (dx + 1) * 10 + (dy + 1)
        score = (lead_after * 10) + (-nds) + (5 if (nx, ny) == (tx, ty) else 0) + tie * 1e-6
        if best_move[0] is None or score > best_move[0]:
            best_move = (score, (dx, dy))

    if best_move[1] is None:
        return [0, 0]
    dx, dy = best_move[1]
    if dx < -1: dx = -1
    if dx > 1: dx = 1
    if dy < -1: dy = -1
    if dy > 1: dy = 1
    return [int(dx), int(dy)]