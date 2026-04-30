def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = observation.get("obstacles", []) or []
    obs = set((p[0], p[1]) for p in obstacles)
    resources = observation.get("resources", []) or []

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def cheb(a, b): return max(abs(a[0]-b[0]), abs(a[1]-b[1]))
    def manh(a, b): return abs(a[0]-b[0]) + abs(a[1]-b[1])

    if not resources:
        tx = 1 if sx < w // 2 else -1 if sx > w // 2 else 0
        ty = 1 if sy < h // 2 else -1 if sy > h // 2 else 0
        return [tx, ty]

    # Local next-step evaluation (obstacle-aware), with deterministic tie-breaks.
    best = None
    best_key = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        # Prefer moving closer (in Chebyshev metric) to the nearest remaining resource.
        d_res = min(cheb((nx, ny), r) for r in resources)
        # Avoid walking towards opponent to reduce chance of them contesting resources.
        d_opp = cheb((nx, ny), (ox, oy))
        # Slightly prefer staying nearer to resources' "mass" centroid to avoid oscillation.
        cx = sum(r[0] for r in resources) / len(resources)
        cy = sum(r[1] for r in resources) / len(resources)
        dist_cent = abs(nx - cx) + abs(ny - cy)

        key = (d_res, -d_opp, dist_cent, manh((nx, ny), (sx, sy)))
        if best_key is None or key < best_key:
            best_key = key
            best = (dx, dy)

    if best is None:
        # All moves blocked by obstacles; deterministically step to any in-bounds unblocked cell or stay.
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obs:
                return [dx, dy]
        return [0, 0]

    return [best[0], best[1]]