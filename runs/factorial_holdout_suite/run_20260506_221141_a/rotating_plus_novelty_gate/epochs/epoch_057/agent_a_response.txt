def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocked = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    resources = []
    seen = set()
    for p in observation.get("resources", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked and (x, y) not in seen:
                resources.append((x, y))
                seen.add((x, y))
    if not resources:
        return [0, 0]

    def kdist(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        ax = dx if dx >= 0 else -dx
        ay = dy if dy >= 0 else -dy
        return ax if ax > ay else ay

    # Choose resource where we have the largest distance advantage.
    best = resources[0]
    best_adv = -10**18
    best_sd = 10**18
    for rx, ry in resources:
        sd = kdist(sx, sy, rx, ry)
        od = kdist(ox, oy, rx, ry)
        adv = od - sd
        if adv > best_adv or (adv == best_adv and (sd < best_sd or (sd == best_sd and (rx, ry) < best))):
            best_adv = adv
            best_sd = sd
            best = (rx, ry)

    rx, ry = best

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    # Deterministic tie-break order: fixed move list.
    def step_score(nx, ny):
        if (nx, ny) in blocked:
            return -10**9
        sd = kdist(nx, ny, rx, ry)
        # Opponent pressure: prefer states where opponent is relatively worse.
        od = kdist(ox, oy, rx, ry)
        # Repel from obstacles (soft)
        obs_rep = 0
        for (bx, by) in blocked:
            dx = nx - bx
            dy = ny - by
            adx = dx if dx >= 0 else -dx
            ady = dy if dy >= 0 else -dy
            d = adx if adx > ady else ady
            if d == 0:
                return -10**9
            if d <= 2:
                obs_rep -= (3 - d) * 5
        # Prefer progress toward target; slight preference for lower sd then higher advantage.
        return (best_adv + od - sd) * 100 - sd + obs_rep

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h:
            v = step_score(nx, ny)
            if v > best_val:
                best_val = v
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]