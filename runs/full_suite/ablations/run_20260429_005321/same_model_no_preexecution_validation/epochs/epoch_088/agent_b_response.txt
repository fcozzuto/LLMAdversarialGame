def choose_move(observation):
    w = int(observation["grid_width"]); h = int(observation["grid_height"])
    sx, sy = int(observation["self_position"][0]), int(observation["self_position"][1])
    ox, oy = int(observation["opponent_position"][0]), int(observation["opponent_position"][1])

    resources = [(int(p[0]), int(p[1])) for p in (observation.get("resources") or [])]
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []))

    dirs = (-1, 0, 1)
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def free(x, y): return inb(x, y) and (x, y) not in obstacles
    def cheb(ax, ay, bx, by):
        dx = ax - bx; dx = -dx if dx < 0 else dx
        dy = ay - by; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy
    def adj_obs(x, y):
        c = 0
        for dx in dirs:
            for dy in dirs:
                if dx == 0 and dy == 0: continue
                if (x + dx, y + dy) in obstacles: c += 1
        return c

    best = None; bestv = -10**18
    for rx, ry in resources:
        dme = cheb(sx, sy, rx, ry)
        dop = cheb(ox, oy, rx, ry)
        # Prefer resources where we can arrive much earlier; break ties by safety/value.
        v = (dop - dme) * 6.0 - dme * 0.8 - 1.1 * adj_obs(rx, ry)
        # Nudge to keep moving "forward" relative to opponent: side advantage
        if ox < w // 2:
            v += 0.35 * (rx - w / 2)
        else:
            v += 0.35 * (w / 2 - rx)
        if dme < dop: v += 3.0
        if v > bestv:
            bestv = v; best = (rx, ry)

    if best is None:
        tx, ty = w // 2, h // 2
    else:
        tx, ty = best

    # Evaluate immediate move deltas deterministically.
    def delta_toward(x, y, tx, ty):
        dx = 0 if tx == x else (1 if tx > x else -1)
        dy = 0 if ty == y else (1 if ty > y else -1)
        return dx, dy

    preferred = delta_toward(sx, sy, tx, ty)
    candidates = []
    for dx in dirs:
        for dy in dirs:
            if dx == 0 and dy == 0:
                candidates.append((0.0, 0, 0))
                continue
            candidates.append((0.0, dx, dy))

    # Score candidates: reach target + avoid obstacles + don't give opponent easy advantage.
    def cand_score(dx, dy):
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny): return -10**18
        dm = cheb(nx, ny, tx, ty)
        da = cheb(ox, oy, tx, ty)
        # If we can keep parity or win, prioritize; otherwise retreat from contested spots slightly.
        contest = (da - dm)
        return contest * 5.0 - dm * 0.7 - 1.0 * adj_obs(nx, ny)

    # Try preferred first to reduce oscillation; then best-scoring fallback.
    pdx, pdy = preferred
    if free(sx + pdx, sy + pdy):
        if cand_score(pdx, pdy) >= cand_score(0, 0) - 0.01:
            return [pdx, pdy]

    bestd = (0, 0); bests = cand_score(0, 0)
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if (dx, dy) == (0, 0): continue
            s = cand_score(dx, dy)
            if s > bests + 1e-9 or (abs(s - bests) <= 1e-9 and (dx, dy) < bestd):
                bests = s; bestd = (dx, dy)
    return [int(bestd[0]), int(bestd[1])]