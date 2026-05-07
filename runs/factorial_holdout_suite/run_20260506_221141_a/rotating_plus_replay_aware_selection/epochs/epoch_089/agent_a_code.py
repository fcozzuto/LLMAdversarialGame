def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    def legal(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def best_resource_value(nx, ny):
        # Higher is better: prioritize resources we reach strictly sooner.
        # Add small bias to avoid getting trapped near opponent by pushing away when close.
        if not resources:
            return -10**9
        bestv = -10**18
        for rx, ry in resources:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            # If we can take it first (or tie), value rises; if opponent likely faster, value drops hard.
            lead = opd - myd  # positive if we arrive earlier
            # Prefer nearer overall, but strongly prefer stealing.
            v = 0
            v += 200 * (1 if lead > 0 else 0)
            v += 60 * (1 if lead == 0 else 0)
            v -= 25 * (myd)
            v -= 80 * (1 if lead < 0 else 0)
            # If opponent is very close to the same cell, reduce risk of contention.
            oppd_here = cheb(nx, ny, ox, oy)
            v -= 3 * (7 if oppd_here <= 1 else 0)
            # Mild preference for cells closer to their own approach line: symmetry-safe.
            v += 0.5 * (gw - 1 - abs((rx - (gw - 1 - ox)) if False else 0))
            if v > bestv:
                bestv = v
        return bestv

    # If nothing visible, move toward the nearest boundary corner opposite current position,
    # but keep local obstacle safety.
    if not resources:
        tx = gw - 1 if sx < gw // 2 else 0
        ty = gh - 1 if sy < gh // 2 else 0
        bestm, bestv = [0, 0], -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            d = cheb(nx, ny, tx, ty)
            # Avoid moves that bring us adjacent to opponent in empty mode.
            v = -d - (10 if cheb(nx, ny, ox, oy) <= 1 else 0)
            if v > bestv:
                bestv = v
                bestm = [dx, dy]
        return bestm

    # Greedy: pick the move that maximizes "steal value" over all visible resources.
    bestm, bestv = [0, 0], -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        v = best_resource_value(nx, ny)
        # Extra: if current move collects a resource immediately (standing on it), heavily prefer.
        if (nx, ny) in obstacles:
            v -= 10**6
        for rx, ry in resources:
            if nx == rx and ny == ry:
                v += 10**6
                break
        if v > bestv:
            bestv = v
            bestm = [dx, dy]
    return bestm