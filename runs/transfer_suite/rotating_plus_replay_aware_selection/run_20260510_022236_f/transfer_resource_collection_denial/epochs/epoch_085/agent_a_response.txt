def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    tr = int(observation.get("turns_remaining", 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set((int(x), int(y)) for x, y in obstacles)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    valid = []
    for rx, ry in resources:
        rx, ry = int(rx), int(ry)
        if inb(rx, ry) and (rx, ry) not in obs:
            valid.append((rx, ry))
    if not valid:
        return [0, 0]

    best = None
    for rx, ry in valid:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # maximize lead; if tied, prefer nearer and earlier-than-turns
        lead = do - ds
        urgency = 0
        if tr > 0 and ds <= tr:
            urgency = 10
        score = lead * 100 + urgency * 5 - ds
        if best is None or score > best[0]:
            best = (score, rx, ry)
    _, tx, ty = best

    # One-step greedy with safety: minimize distance-to-target; if tie, maximize target lead;
    # if blocked/invalid, engine will keep us, so also avoid moves that land on obstacles.
    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue  # keep still as fallback if no move improves
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obs:
                continue
            dnext = cheb(nx, ny, tx, ty)
            # compute opponent lead using same target
            onext = cheb(ox, oy, tx, ty)  # opponent might move, but deterministic heuristic uses current dist
            cand_score = -dnext * 10 + (onext - dnext)  # higher is better
            candidates.append((cand_score, dx, dy))
    if candidates:
        candidates.sort(reverse=True)
        return [int(candidates[0][1]), int(candidates[0][2])]
    return [0, 0]