def choose_move(observation):
    w = observation.get("grid_width", 8); h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) == 2:
            obstacles.add((p[0], p[1]))
    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2; dx = -dx if dx < 0 else dx
        dy = y1 - y2; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy

    def dist2(x1, y1, x2, y2):
        dx = x1 - x2; dy = y1 - y2
        return dx * dx + dy * dy

    opp_corner = (0, 0) if (ox, oy) == (w - 1, h - 1) else (w - 1, h - 1)
    best = (-10**18, 0, 0)

    # Precompute nearest resource to guide motion deterministically
    if resources:
        res_sorted = sorted(resources, key=lambda r: (dist2(sx, sy, r[0], r[1]), r[0], r[1]))
        r0 = res_sorted[0]
        target = (r0[0], r0[1])
    else:
        target = opp_corner

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue

        # Avoid edges early to prevent getting boxed; later become bolder by turn index
        t = observation.get("turn_index", 0)
        edge_weight = 0.8 if t < 10 else 0.2
        edge = (1 if nx == 0 else 0) + (1 if nx == w - 1 else 0) + (1 if ny == 0 else 0) + (1 if ny == h - 1 else 0)

        # Goal: approach target resource; if resource exists, also keep a little distance from opponent
        d_target = cheb(nx, ny, target[0], target[1])
        d_opp = cheb(nx, ny, ox, oy)

        # If we can take a resource immediately, prioritize it strongly and penalize giving opponent same chance
        if resources and (nx, ny) in set(map(tuple, resources)):
            immediate = 50.0
        else:
            immediate = 0.0

        # Interception: move along the direction that reduces (dx,dy) to opponent capture line (in Chebyshev)
        # Prefer being nearer to opponent when resources are scarce.
        scarcity = 1.0
        rem = observation.get("remaining_resource_count", len(resources))
        if rem is not None:
            scarcity = 1.0 if rem > 6 else (0.8 if rem > 3 else 1.4)

        # Obstacle-aware: mild penalty if moving adjacent to obstacles (reduces chance of dead-ends)
        adj_obs = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                px, py = nx + ax, ny + ay
                if (px, py) in obstacles:
                    adj_obs += 1

        # Opponent pressure term: when close to a resource, keep distance; otherwise consider corner pressure
        if resources:
            opp_term = (d_opp * 0.15) if d_target <= 2 else (-d_opp * 0.05)
        else:
            opp_term = (-cheb(nx, ny, ox, oy) * 0.25)

        score = (
            -d_target
            + immediate
            - edge_weight * edge
            - 0.03 * adj_obs
            + opp_term * scarcity
            + 0.01 * (nx - ny)  # deterministic tie-break
        )

        if score > best[0] or (score == best[0] and (dx, dy) < (best[1], best[2])):
            best = (score, dx, dy)

    return [best[1], best[2]] if best else [0, 0]