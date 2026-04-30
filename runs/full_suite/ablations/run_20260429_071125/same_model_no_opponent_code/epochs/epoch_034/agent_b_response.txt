def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    best = None
    for rx, ry in resources:
        du = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        adv = do - du  # positive => we can arrive earlier
        # Prefer a decisive advantage; otherwise contest nearest to opponent by maximizing our proximity gain.
        # Tie-break deterministically by farther-from-opponent-first to avoid "mirror" stalling.
        cand = (adv, du, -do, -rx, -ry)
        if best is None or cand > best:
            best = cand
    _, _, _, tx, ty = best

    candidates = []
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            d_to = cheb(nx, ny, tx, ty)
            margin = cheb(ox, oy, tx, ty) - cheb(nx, ny, tx, ty)
            # minimize distance; maximize margin; deterministic tie-break by position
            score = (d_to, -margin, nx, ny)
            candidates.append((score, dx, dy))
    candidates.sort()
    return [int(candidates[0][1]), int(candidates[0][2])]