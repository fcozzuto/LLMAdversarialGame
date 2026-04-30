def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = int(observation["self_position"][0]), int(observation["self_position"][1])
    ox, oy = int(observation["opponent_position"][0]), int(observation["opponent_position"][1])

    resources = [(int(p[0]), int(p[1])) for p in (observation["resources"] or [])]
    obstacles = set((int(p[0]), int(p[1])) for p in (observation["obstacles"] or []))

    dirs = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def adj_obs(x, y):
        c = 0
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if (nx, ny) in obstacles:
                c += 1
        return c

    def toward_delta(x, y, tx, ty):
        dx = 0 if tx == x else (1 if tx > x else -1)
        dy = 0 if ty == y else (1 if ty > y else -1)
        return [dx, dy]

    def best_target():
        if not resources:
            return (w // 2, h // 2)
        # Materially different from a pure distance-only rule:
        # Primary: how much earlier we can reach than opponent.
        # Secondary: prefer resources on our "side" relative to opponent to reduce contention.
        best = resources[0]
        bestv = -10**18
        mySide = 1 if sx <= w // 2 else -1
        opSide = 1 if ox <= w // 2 else -1
        for rx, ry in resources:
            dme = cheb(sx, sy, rx, ry)
            dop = cheb(ox, oy, rx, ry)
            lead = dop - dme  # positive means we are earlier
            side_bias = (1 if ((rx <= w // 2) == (mySide == 1)) else -1) * 0.8
            # If opponent is closer, strongly avoid crowded/adjacent-to-obstacle targets
            obs_pen = adj_obs(rx, ry) * (2.6 if dme >= dop else 1.2)
            # Slightly prefer deeper targets (harder to contest)
            depth = (abs(rx - ox) + abs(ry - oy)) * 0.03
            v = lead * 120.0 + side_bias * 10.0 - obs_pen - depth
            # Deterministic tie-break: lexicographic by (rx, ry)
            if v > bestv or (v == bestv and (rx, ry) < best):
                bestv = v
                best = (rx, ry)
        return best

    tx, ty = best_target()

    # Determine posture: if behind, play safer (distance-maximizing); if ahead, push (distance-minimizing).
    dme_now = cheb(s