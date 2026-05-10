def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles", []) or []))
    resources = observation.get("resources", []) or []
    resources = [(int(r[0]), int(r[1])) for r in resources]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    if not resources:
        # Fallback: approach farthest corner from opponent to reduce contesting
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        tx, ty = corners[0]
        bestc = -1
        for cx, cy in corners:
            d = cheb(cx, cy, ox, oy)
            if d > bestc:
                bestc = d
                tx, ty = cx, cy
        bestm = [0, 0]
        best = -10**9
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            sc = -cheb(nx, ny, tx, ty) + 0.001 * cheb(nx, ny, ox, oy)
            if sc > best:
                best = sc
                bestm = [dx, dy]
        return bestm

    # 1-step lookahead: choose move maximizing our best "win-urgency" for any resource.
    best_move = [0, 0]
    best_val = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        my_best = -10**18
        # Compare our distance from (nx,ny) vs opponent distance from current (ox,oy).
        for rx, ry in resources:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            adv = opd - myd  # positive means we can arrive no later than opponent
            # Tie-break: prefer non-losing (adv>=0), then larger adv, then smaller myd, then deterministic coords
            # Keep deterministic ordering via rx,ry.
            val = (0 if adv < 0 else 1) * 10**7 + adv * 10**5 - myd * 100 - rx * 0.01 - ry * 0.001
            if val > my_best:
                my_best = val
        # Add small bias to move towards staying capable if close calls; also reduce collisions risk by preferring central-ish.
        center_bias = -abs(nx - (w - 1) / 2) * 0.0001 - abs(ny - (h - 1) / 2) * 0.0001
        total = my_best + center_bias
        if total > best_val:
            best_val = total
            best_move = [dx, dy]
    return best_move