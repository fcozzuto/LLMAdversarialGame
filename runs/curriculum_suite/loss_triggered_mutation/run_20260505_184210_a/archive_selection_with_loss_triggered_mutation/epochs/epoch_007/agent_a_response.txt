def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set((p[0], p[1]) for p in observation.get("obstacles", []))
    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(a, b):
        return max(abs(a[0]-b[0]), abs(a[1]-b[1]))

    def step_options(cx, cy):
        opts = []
        for dx, dy in deltas:
            nx, ny = cx + dx, cy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                opts.append((nx, ny, dx, dy))
        return opts if opts else [(cx, cy, 0, 0)]

    def best_resource_for_pos(px, py):
        # Score for taking a resource: prefer we arrive earlier; also prefer closer resource and (slightly) farther from opponent.
        best = None
        for rx, ry in resources:
            ds = cheb((px, py), (rx, ry))
            do = cheb((ox, oy), (rx, ry))
            adv = do - ds  # positive => we are earlier (or at least closer in turns)
            tie = -ds
            opp = -do
            center = -((rx - (w-1)/2) ** 2 + (ry - (h-1)/2) ** 2) * 1e-3
            val = (adv * 1000) + tie * 10 + opp + center
            if (best is None) or (val > best[0]):
                best = (val, rx, ry)
        return best[1:] if best else None

    opts = step_options(sx, sy)
    if resources:
        target = best_resource_for_pos(sx, sy)
        if target:
            tx, ty = target
            # Also consider opponent pressure: occasionally block by moving toward resources opponent is closer to.
            best_move = None
            for nx, ny, dx, dy in opts:
                my = cheb((nx, ny), (tx, ty))
                opp_to = cheb((ox, oy), (tx, ty))
                # If we can secure the target sooner than opponent, prioritize; else reduce opponent advantage.
                score = (opp_to - my) * 1000 - my * 2
                # Small term to keep distance to opponent if we're not winning the target.
                if (opp_to - my) <= 0:
                    score -= cheb((nx, ny), (ox, oy)) * 0.5
                # Prefer moves that are not obviously worsening adjacency to nearby resources.
                for rx, ry in resources:
                    if cheb((nx, ny), (rx, ry)) == 1:
                        score += 3
                if (best_move is None) or (score > best_move[0]):
                    best_move = (score, dx, dy)
            return [best_move[1], best_move[2]]

    # Fallback: go toward nearest resource, else toward center while avoiding obstacles.
    if resources:
        nearest = min(resources, key=lambda r: cheb((sx, sy), (r[0], r[1])))
        tx, ty = nearest
    else:
        tx, ty = (w - 1) / 2, (h - 1) / 2
    best_move = None
    for nx, ny, dx, dy in opts:
        d = cheb((nx, ny), (tx, ty))
        # Discourage moving into squares that make us stuck by heavily weighting proximity to obstacles.
        adj = 0
        for ddx, ddy in deltas:
            ax, ay = nx + ddx, ny + ddy
            if inb(ax, ay) and (ax, ay) in obstacles:
                adj += 1
        score = -d * 10 - adj * 0.8
        # If we can step to match resource line, prioritize.
        for rx, ry in resources:
            if cheb((nx, ny), (rx, ry)) == 0:
                score += 1000
        if (best_move is None) or (score > best_move[0]):
            best_move = (score, dx, dy)
    return [best_move[1], best_move[2]]