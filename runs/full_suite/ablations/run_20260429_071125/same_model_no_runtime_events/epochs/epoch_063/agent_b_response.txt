def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        return [0, 0]

    best_resources = []
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        # Prioritize resources where we're at least as close; break ties by closeness.
        score = (1 if myd <= opd else 0) * 10_000 - (myd * 10 + opd)
        best_resources.append((score, rx, ry))
    best_resources.sort(reverse=True)
    targets = best_resources[:4]  # small deterministic set

    oppdist = cheb(sx, sy, ox, oy)
    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        # Avoid walking into opponent by trying to keep/extend distance.
        new_oppdist = cheb(nx, ny, ox, oy)
        opp_keep = new_oppdist - oppdist

        # Choose the target that best improves our lead.
        best_tar = -10**18
        for _, rx, ry in targets:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            # Lead = opponent distance - our distance (larger is better).
            lead = opd - myd
            # Prefer quicker capture when lead is similar.
            val = lead * 1000 - myd * 3
            # Slightly discourage moving toward a resource if opponent is extremely close to it.
            if opd <= myd:
                val -= (myd - opd) * 20
            if val > best_tar:
                best_tar = val

        # Small tie-break: prefer diagonal/axis move that reduces my nearest distance to any resource.
        nearest_before = min(cheb(sx, sy, rx, ry) for _, rx, ry in best_resources)
        nearest_after = min(cheb(nx, ny, rx, ry) for _, rx, ry in best_resources)
        my_reduce = nearest_before - nearest_after

        total = best_tar + opp_keep * 8 + my_reduce
        if total > best_val:
            best_val = total
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]