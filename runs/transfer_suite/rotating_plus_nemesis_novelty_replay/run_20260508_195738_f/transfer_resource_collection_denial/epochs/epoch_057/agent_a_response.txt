def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles", []) or []))
    resources = [(int(r[0]), int(r[1])) for r in (observation.get("resources", []) or [])]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(a, b, c, d):
        dx = abs(a - c)
        dy = abs(b - d)
        return dx if dx > dy else dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        tx, ty = max(corners, key=lambda c: (cheb(ox, oy, c[0], c[1]), -c[0], -c[1]))
        best, bestmv = (-10**9, (0, 0))
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            v = -cheb(nx, ny, tx, ty) - 0.05 * cheb(nx, ny, ox, oy)
            if v > best:
                best, bestmv = v, (dx, dy)
        return [bestmv[0], bestmv[1]]

    # Evaluate moves by the best "resource race" advantage after moving.
    def best_race(nx, ny):
        best = (-10**9, None)
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Prefer cells we can reach sooner than opponent, break ties by closeness.
            v = (do - ds) * 1000 - ds
            # Mild bias toward targets closer overall (reduces dithering).
            v += -0.001 * (abs(rx - ox) + abs(ry - oy))
            if v > best[0]:
                best = (v, (rx, ry))
        return best[0]

    best, bestmv = (-10**9, (0, 0))
    # Small lookahead: if we can immediately collect (on resource), strongly prefer it.
    resource_set = set(resources)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        immediate = 200000 if (nx, ny) in resource_set else 0
        v = immediate + best_race(nx, ny)
        # Defensive tie-break: if equal, move that reduces opponent-to-resources distance.
        if v > best:
            best, bestmv = v, (dx, dy)
        elif v == best:
            curr_opp = min(cheb(ox, oy, rx, ry) for rx, ry in resources)
            nxt_opp = min(cheb(ox, oy, rx, ry) for rx, ry in resources)  # opponent pos unchanged in this step
            if nxt_opp < curr_opp:
                bestmv = (dx, dy)
            else:
                # deterministic tie-break by dx,dy ordering already stable; keep current
                pass
    return [bestmv[0], bestmv[1]]