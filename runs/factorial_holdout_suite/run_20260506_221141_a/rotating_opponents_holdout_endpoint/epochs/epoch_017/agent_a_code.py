def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    # If no resources, drift toward center while avoiding obstacles.
    if not resources:
        best = (-10**18, 0, 0)
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            score = -((nx - cx) ** 2 + (ny - cy) ** 2)
            if (nx, ny) in obstacles:
                score -= 10**6
            if score > best[0]:
                best = (score, dx, dy)
        return [best[1], best[2]]

    # Evaluate each candidate next cell by best advantage over opponent among resources.
    best = (-10**18, 0, 0)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        # Obstacle proximity penalty.
        prox = 0
        for ax, ay in obstacles:
            d = man(nx, ny, ax, ay)
            if d == 0:
                prox += 50
            elif d == 1:
                prox += 6
            elif d == 2:
                prox += 2

        self_score = 0
        for rx, ry in resources:
            ds = man(nx, ny, rx, ry)
            do = man(ox, oy, rx, ry)
            # Want do - ds positive (we reach earlier), then prefer smaller ds.
            advantage = (do - ds)
            # Slight tie-break: prefer closer to resource and avoid over-commit to worse nodes.
            val = advantage * 100 - ds
            if val > self_score:
                self_score = val

        # Mild anti-collision: don't move to let opponent immediately grab an "equally good" cell.
        opp_reach = min((man(ox, oy, rx, ry) for rx, ry in resources), default=0)
        my_reach = min((man(nx, ny, rx, ry) for rx, ry in resources), default=0)
        anti = -max(0, my_reach - opp_reach) * 5

        # Prefer staying/advancing when scores tie deterministically.
        center_bias = -((nx - cx) ** 2 + (ny - cy) ** 2) * 0.001
        score = self_score + anti + center_bias - prox

        # Deterministic tie-break: prefer moves that keep x then y direction order.
        if score > best[0]:
            best = (score, dx, dy)
        elif score == best[0]:
            if (dx, dy) < (best[1], best[2]):
                best = (score, dx, dy)

    return [best[1], best[2]]